# Lesson 8: Logic Vulnerability (Race Condition)

> DVSA Security Lesson – Educational Purpose Only

---

## Overview

This lesson demonstrates a **Logic Vulnerability (Race Condition)** in the DVSA order-processing workflow.

The issue occurs because the system does not lock the order during billing, allowing multiple requests to execute simultaneously and modify the order state during payment processing.

---

## Summary

An attacker can send two requests at the same time:

* Billing request (payment)
* Update request (modify cart)

### Result

* The system charges based on old data
* The cart is updated during processing
* The user pays less but receives more items

---

## Root Cause

The system checks:

```
if status < 120
```

But does NOT:

* Lock the order
* Prevent concurrent updates

This creates a race condition between:

* Billing request
* Update request

---

## Impact

* Incorrect billing
* Data inconsistency
* Business logic failure
* Users receive more than they paid for

---

## Setup

* DVSA URL:
  http://dvsa-website4-128066560383-us-east-1.s3-website-us-east-1.amazonaws.com

* API Endpoint:
  https://jg71b5i888.execute-api.us-east-1.amazonaws.com/dvsa/order

* Lambda Function:
  DVSA-ORDER-BILLING

* Tools:

  * Python 3
  * threading
  * requests
  * AWS Console
  * CloudWatch

---


This project is for educational purposes only using DVSA.
Do not test on real systems without permission.
