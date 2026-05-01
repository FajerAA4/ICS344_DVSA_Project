# Lesson 6: Denial of Service (DoS)

> DVSA Security Lesson – Educational Purpose Only

---

## Overview

This lesson demonstrates a **Denial of Service (DoS)** vulnerability in the DVSA billing endpoint.

The vulnerability exists because the API Gateway does not enforce rate limiting, allowing attackers to send a large number of requests in a short time, overwhelming the backend Lambda function.

---

## Vulnerability

- No rate limiting on API Gateway
- Unlimited concurrent requests allowed
- Lambda function can be overloaded

---

## Impact

- Lambda crashes under load
- API Gateway returns 500/502 errors
- Service becomes unavailable for legitimate users

---

## Root Cause

- API Gateway configured with:
  - Rate: 10,000 requests/sec
  - Burst: 5,000
- No throttling per user
- No protection against abuse

---

## Fix

- Enable throttling in API Gateway
- Reduce rate to 10 requests/sec
- Set burst limit to 20

---

## Result

- Excess requests blocked
- API returns 429 Too Many Requests
- Lambda protected from overload

---

## Folder Structure
