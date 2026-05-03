# ICS 344 DVSA Vulnerability Discovery and Remediation Project
## Team Members
- Afrah Alsubhi
- Fajer Alyami

## Course Information
- Course: ICS 344 – Information Security
- Term: 252

# DVSA Serverless Security — ICS344 Project

This repository documents ten serverless security lessons performed on the **OWASP DVSA (Damn Vulnerable Serverless Application)** as part of ICS-344: Information Security at KFUPM. For each lesson we identify a vulnerability in the deployed AWS environment, demonstrate the exploit, apply a fix, and verify the fix works without breaking legitimate functionality.

**Environment:** AWS `us-east-1`, OWASP DVSA deployed via Serverless Application Repository

> Note: DVSA is intentionally vulnerable and must only be deployed in a non-production AWS account. This repository is for educational use within ICS-344. Do not apply these techniques to systems you do not own.

---

## The 10 Lessons

| # | Lesson | Vulnerability | Component | Fix Type |
|---|---|---|---|---|
| [1](./lesson-01-event-injection-vulnerable-dep) | Event Injection / Vulnerable Dependencies | RCE via `node-serialize` deserialization of attacker-controlled input | `DVSA-ORDER-MANAGER` Lambda | Code: replace `serialize.unserialize()` with `JSON.parse()` |
| 2 | Broken Authentication | JWT payload trusted without signature verification → user impersonation | `DVSA-ORDER-MANAGER` Lambda | Code: verify Cognito JWT signature, validate `iss` / `exp` / `token_use` claims |
| [3](./lesson-03-sensitive-info-disclosure) | Sensitive Information Disclosure | Receipt-archive Lambda generates pre-signed S3 URLs without authorization check | `DVSA-ADMIN-GET-RECEIPT` Lambda | Code: add admin check at top of handler |
| 4 | Insecure Cloud Configuration | S3 receipts bucket allowed public uploads, triggering backend Lambda automatically | S3 bucket policy | Config: enable Block Public Access, restrict writes to DVSA roles |
| [5](./lesson-05-broken-access-control) | Broken Access Control | Admin-only Lambda accepted non-admin tokens → unauthorized order updates | `DVSA-ADMIN-UPDATE-ORDERS` Lambda | Code: add JWT scope check requiring `admin` |
| 6 | Denial of Service (DoS) | API Gateway had no rate limiting → 50 concurrent requests crashed Lambda | API Gateway stage | Config: enable throttling (10 req/sec, burst 20) |
| [7](./lesson-07-overprivileged-iam) | Over-Privileged IAM Role | Lambda execution role had wildcard access to S3 and DynamoDB | `DVSA-SEND-RECEIPT-EMAIL` IAM role | Config: remove wildcard policies, attach minimal SES-only policy |
| 8 | Logic Vulnerability (Race Condition) | Billing function did not lock order state → concurrent update during payment | `DVSA-ORDER-BILLING` Lambda | Code: add DynamoDB `ConditionExpression` lock before cart total |
| [9](./lesson-09-vulnerable-dependencies) | Vulnerable Dependencies | `node-serialize` (no patch available) enabled RCE | `DVSA-ORDER-MANAGER` Lambda | Code: remove `node-serialize`, use `JSON.parse()` |
| 10 | Unhandled Exceptions | Missing input validation/exception handling leaked stack traces and file paths | `DVSA-ORDER-BILLING` Lambda | Code: add input validation + generic error responses |

> Lessons linked above (1, 3, 5, 7, 9) have full standalone walkthroughs in their own folders. The remaining lessons (2, 4, 6, 8, 10) are summarized below and documented in the main project report.

---

## How this repo is organized

```
dvsa-lessons/
├── README.md                                       ← this file
├── lesson-01-event-injection-vulnerable-dep/      ← full walkthrough
├── lesson-02-broken-authentication/               ← summary + analysis tables
├── lesson-03-sensitive-info-disclosure/           ← full walkthrough
├── lesson-04-insecure-cloud-config/               ← summary + analysis tables
├── lesson-05-broken-access-control/               ← full walkthrough
├── lesson-06-denial-of-service/                   ← summary + analysis tables
├── lesson-07-overprivileged-iam/                  ← full walkthrough
├── lesson-08-logic-race-condition/                ← summary + analysis tables
├── lesson-09-vulnerable-dependencies/             ← full walkthrough
└── lesson-10-unhandled-exceptions/                ← summary + analysis tables
```

Each lesson folder contains:

```
lesson-XX-name/
├── README.md          ← walkthrough: setup, exploit, fix, verification, analysis
├── screenshots/       ← numbered evidence images, in narrative order
└── code/              ← exploit scripts, vulnerable code, patched code, IAM policies
```

---

## Lesson summaries

### Lesson 1 — Event Injection / Vulnerable Dependencies
The `DVSA-ORDER-MANAGER` Lambda passed the raw HTTP body to the legacy `node-serialize` library. A payload using the `_$$ND_FUNC$$_` marker was deserialized as a JavaScript function and executed inside Lambda, achieving Remote Code Execution. Fix: replace `serialize.unserialize()` with `JSON.parse()`. **[Full walkthrough →](./lesson-01-event-injection-vulnerable-dep)**

### Lesson 2 — Broken Authentication
The backend decoded JWT payloads and trusted `username`/`sub` claims without verifying the token signature. An attacker could modify the payload of their own valid JWT, replace identity fields with another user's, and access the victim's order list and details. Fix: introduce `verifyCognitoJwt()` to validate the signature against AWS Cognito public keys and check `iss`, `exp`, and `token_use` claims before extracting any identity.

### Lesson 3 — Sensitive Information Disclosure
The `DVSA-ADMIN-GET-RECEIPT` Lambda built a ZIP of receipts based on user-supplied `year`/`month` and returned a pre-signed S3 URL — with no authorization check. Any caller could download every receipt in the system. Fix: add an admin check at the top of the handler so non-admins are rejected before any S3 access happens. **[Full walkthrough →](./lesson-03-sensitive-info-disclosure)**

### Lesson 4 — Insecure Cloud Configuration
The DVSA receipts S3 bucket had "Block all public access" disabled. Any unauthenticated user could upload arbitrary files via `aws s3 cp ... --acl public-read`, and the upload automatically triggered the `DVSA-SEND-RECEIPT-EMAIL` Lambda through an Object Created event. Fix: re-enable Block Public Access and restrict bucket writes to the DVSA execution role only. No code change needed — configuration hardening alone solves it.

### Lesson 5 — Broken Access Control
`DVSA-ADMIN-UPDATE-ORDERS` validated JWT structure but never checked the `scope` claim, so any authenticated user could invoke the admin function via the AWS Console Test tab and flip an order from `processed` to `paid` without paying. Fix: add a server-side scope check (`if "admin" not in scope.lower().split()`) at the top of the handler. **[Full walkthrough →](./lesson-05-broken-access-control)**

### Lesson 6 — Denial of Service (DoS)
The API Gateway stage was configured with the default 10,000 req/sec rate and 5,000 burst, with no per-user throttling. A Python script sending 50 concurrent billing requests overwhelmed the `DVSA-ORDER-BILLING` Lambda, producing 500/502 errors. Fix: enable throttling on the `dvsa` stage at 10 req/sec, burst 20. After the fix the same attack returns 429 Too Many Requests instead of crashing the function.

### Lesson 7 — Over-Privileged IAM Role
The execution role for `DVSA-SEND-RECEIPT-EMAIL` had wildcard permissions on S3 (`arn:aws:s3:::*`) and DynamoDB (`table/*`), plus the AWS-managed `AmazonSESFullAccess`. The IAM Policy Simulator confirmed the role could read/write any object or table in the account. Fix: remove the wildcard inline policies and `AmazonSESFullAccess`, attach a minimal custom policy allowing only `ses:SendEmail` and `ses:SendRawEmail`. **[Full walkthrough →](./lesson-07-overprivileged-iam)**

### Lesson 8 — Logic Vulnerability (Race Condition)
The `DVSA-ORDER-BILLING` Lambda checked `if status < 120` but did not lock the order before computing the cart total. A concurrent `update` request could change the cart contents while billing was still calculating the price, so the customer paid for one quantity but received another. Fix: add a DynamoDB `ConditionExpression` lock that atomically marks the order as `processing` before the cart total is read. After the fix, concurrent update requests return `order already paid`.

### Lesson 9 — Vulnerable Dependencies
Same root cause as Lesson 1, viewed from the dependency-management angle. `npm audit` flagged `node-serialize` as critical-severity ([GHSA-q4v7-4rhw-9hqm](https://github.com/advisories/GHSA-q4v7-4rhw-9hqm)) with no fix available. The library must be removed entirely — there is no safe version to upgrade to. Fix: replace all `serialize.unserialize()` calls with `JSON.parse()` and run `npm uninstall node-serialize`. **[Full walkthrough →](./lesson-09-vulnerable-dependencies)**

### Lesson 10 — Unhandled Exceptions
`DVSA-ORDER-BILLING` accessed `event["billing"]` directly with no key check, raising a `KeyError` for malformed requests. With no `try/except` wrapping the handler, the Lambda runtime returned the full Python exception — including the file path `/var/task/order_billing.py`, line number 103, source-code snippet, exception type, and missing key name — straight back to the client through API Gateway. Fix: validate the presence of required fields (`orderId`, `user`, `billing`, `ccn`, `exp`, `cvv`) at the start of the handler and return a generic `{"status": "err", "msg": "invalid request"}` if anything is missing.

---

## Environment

- **AWS Region:** `us-east-1`
- **Deployment source:** OWASP DVSA Serverless Repository
- **Tools used across lessons:** AWS Console, AWS CloudShell, CloudWatch Logs, IAM Policy Simulator, PowerShell, Git Bash, `curl`, Python 3 (with `threading`, `requests`), `npm audit`, `jq`

## How to follow along

1. Deploy DVSA into a sandbox AWS account via the Serverless Application Repository (search "DVSA").
2. Pick any lesson folder and open its `README.md`.
3. The "Steps to reproduce" section in each README walks through the exploit.
4. The "Fix" section explains where the change applies (Lambda code, IAM policy, or AWS service config).
5. The "Verification" section shows how to confirm the fix works without breaking legitimate functionality.
