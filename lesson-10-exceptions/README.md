# Lesson 10: Unhandled Exceptions

> DVSA Security Lesson – Educational Purpose Only

---

## Overview

This lesson demonstrates an **Unhandled Exceptions vulnerability** in a serverless AWS Lambda function used in the DVSA application.

The issue occurs when the backend does not properly validate input or handle exceptions, causing the system to expose internal error details such as stack traces, file paths, and source code.

---

## Summary

When a malformed request is sent (missing required fields), the Lambda function crashes with a **KeyError**.

Instead of returning a safe error message, the system exposes:

* Internal file path
* Source code line
* Stack trace
* Exception type

 This leads to **information disclosure** and helps attackers understand the system.

---

## Root Cause

The vulnerability is caused by two main issues:

### 1. No Input Validation

The code directly accesses:

```python
event["billing"]
```

If the key does not exist → Python raises:

```id="a1k2p3"
KeyError
```

---

### 2. No Exception Handling

* No `try/except` block
* Lambda runtime returns full error details
* API Gateway exposes internal debugging information

---

## Setup

* Application: DVSA
* AWS Service: AWS Lambda
* Lambda Function: DVSA-ORDER-BILLING
* File: order_billing.py
* API Endpoint: `/order`
* Tools:

  * Git Bash
  * curl

---


