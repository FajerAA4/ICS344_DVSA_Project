
# Lesson Two: Broken Authentication — JWT Manipulation Vulnerability

> **DVSA Security Research | Educational Purpose Only**

---

## Overview

This report demonstrates a **Broken Authentication** vulnerability found in the [DVSA (Damn Vulnerable Serverless Application)]. The vulnerability is caused by improper JWT validation, where the backend trusts identity claims inside the token payload **without verifying the token signature**.

An attacker can modify the JWT payload and impersonate another user, gaining unauthorized access to that user's order data.

---

## Table of Contents

- [Summary](#summary)
- [Root Cause](#root-cause)
- [Setup](#setup)
- [Steps to Reproduce](#steps-to-reproduce)
- [Evidence](#evidence)
- [Fix Strategy](#fix-strategy)
- [Code Changes](#code-changes)
- [Verification](#verification)
- [Analysis Tables](#analysis-tables)
- [Takeaway](#takeaway)

---

## Summary

This lesson demonstrates a broken authentication vulnerability caused by improper JWT validation. The backend trusts identity claims inside the token payload without properly verifying the token signature. As a result, an attacker can modify the JWT payload and impersonate another user, which leads to **unauthorized access to that user's order data**.

---

## Root Cause

The root cause is that the backend decodes the JWT payload and trusts identity fields such as `username` and `sub` **without verifying the token signature** and required claims. Because the token integrity is not validated, an attacker can alter the payload and reuse the token to impersonate another user.

---

## Setup

- DVSA was deployed and reachable through the browser.
- Two non-admin users were created:
  - **User B** — the attacker
  - **User C** — the victim
- Both users placed at least one order.
- Tools used:
  - Browser Developer Tools
  - `curl`
  - `python3`
  - `jq`
- The Orders API endpoint was identified from the browser request.

---

## Steps to Reproduce

1. Created two non-admin users in DVSA: **User B** (attacker) and **User C** (victim).
2. Logged in with each account and placed at least one order.
3. Opened the Orders page for User B and captured the **request URL** and **Authorization token** from DevTools.
4. Repeated the same process for User C to obtain the victim's identity claims.
5. Decoded both JWT payloads to identify the `username` and `sub` values.
6. Verified normal behavior using User B's valid token to request the order list (only User B's orders returned).
7. **Forged** a new token by modifying User B's JWT payload, replacing the `username` and `sub` fields with User C's identity.
8. Sent a request to the Orders API using the forged token.
9. Observed that the API returned **User C's order list and full order details**, confirming unauthorized access.

---

## Evidence

See the [`/evidence`](./evidence/) directory for screenshots and terminal output.

| # | File | Description |
|---|------|-------------|
| 1 | `01_devtools_request.png` | DevTools showing `/order` API request and request headers |
| 2 | `02_jwt_decode_script.png` | Python script decoding JWT tokens from environment variables (`TOKEN_B`, `TOKEN_C`) |
| 3 | `03_normal_behavior.png` | Valid token returns only User B's orders (expected behavior) |
| 4 | `04_forged_token_exploit.png` | Forged token returns User C's order list — unauthorized access confirmed |
| 5 | `05_order_details.png` | Full victim order details exposed (name, address, phone, email, order ID, etc.) |

### Decoded JWT Fields

```
TOKEN_B:
  username : a4187468-90b1-7021-f735-9371b169e49e
  sub      : a4187468-90b1-7021-f735-9371b169e49e

TOKEN_C:
  username : 04b8e488-b0b1-700a-7b79-6757957d3d4f
  sub      : 04b8e488-b0b1-700a-7b79-6757957d3d4f
```

---

## Fix Strategy

To resolve the broken authentication vulnerability, the backend JWT handling logic was modified to enforce proper token verification **before** trusting any identity claims.

### Changes Applied

- The application **no longer directly decodes the JWT payload** to extract user identity.
- A secure verification function (`verifyCognitoJwt`) was introduced to validate the JWT signature using **trusted public keys from AWS Cognito**.
- The backend now verifies critical claims:
  - `issuer` (`iss`)
  - `expiration` (`exp`)
  - `token_use`
- The `Authorization` header is processed to extract the JWT and remove the `Bearer` prefix before verification.
- User identity (`username` or `sub`) is only extracted **after successful validation** of the token.
- A `.catch()` block was added to handle invalid or tampered tokens, returning a **401 Unauthorized** response instead of processing the request.
- Additional input handling improvements were applied to prevent runtime errors caused by incorrect data types (e.g., converting `isAdmin` safely to string before processing).

---

## Code Changes

See [`/fix`](./fix/) for the patched handler code.

The vulnerable JWT handling logic was replaced with a secure implementation that verifies the token before extracting any identity information.

### Summary of Changes

| Area | Change |
|------|--------|
| JWT extraction | Extract from `Authorization` header, strip `Bearer` prefix |
| Verification | `verifyCognitoJwt` validates signature with AWS Cognito public keys |
| Claims validated | `iss`, `exp`, `token_use` |
| Identity extraction | Only after successful verification |
| Error handling | `.catch()` returns 401 Unauthorized for tampered/invalid tokens |
| Input safety | `isAdmin` converted to string to prevent runtime errors |

---

## Verification

After applying the fix, the system was tested using both **valid** and **forged** tokens.

### Results

| Test | Result |
|------|--------|
| Valid token | Returns correct user's order data |
| Forged token (old exploit) | Rejected by backend |
| Response on forged token | `{"status":"err","msg":"Invalid token"}` |

> **This confirms that the vulnerability has been successfully mitigated.**

---

## Analysis Tables

### Table A — Vulnerability Summary

| Vulnerability | Intended Rule | Artifacts Used | Normal Behavior Evidence | Exploit Behavior Evidence |
|---|---|---|---|---|
| Broken Authentication | Only a valid and verified JWT should determine user identity. Users must not access other users' data | DevTools request headers, JWT payload decoding, API responses | User B sees only his own orders using a valid token | Forged token allows access to User C's orders and order details |

### Table B — Deviation & Fix

| Vulnerability | Why This Is a Deviation | Deviation Class | Fix Applied | Post-Fix Verification |
|---|---|---|---|---|
| Broken Authentication | The backend trusted attacker-controlled JWT claims without verifying token integrity, allowing identity manipulation and unauthorized data access | Intentional misuse / security-relevant abuse | JWT signature verification and claim validation implemented in backend | Forged tokens are rejected, and valid tokens return only correct user data |

---

## Takeaway

**Broken JWT validation** is a critical security flaw that enables user impersonation and unauthorized data access. In this case, modifying token claims allowed the attacker to access another user's order data without proper authorization. This highlights the importance of **verifying token integrity before trusting any identity information**.

In serverless architectures, this issue is even more severe because once an incorrect identity is accepted, all downstream services may execute actions on behalf of the wrong user — potentially cascading unauthorized access across the entire system.

