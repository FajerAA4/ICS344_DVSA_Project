# Lesson 4: Insecure Cloud Configuration

> DVSA Security Lesson – Educational Purpose Only

---

## Overview

This lesson demonstrates an **Insecure Cloud Configuration** vulnerability in DVSA where the S3 bucket was publicly writable.

Because **"Block all public access" was disabled**, any unauthenticated user could upload files to the bucket, which automatically triggered a backend Lambda function.

---

## Vulnerability

- Public write access on S3 bucket
- No authentication required
- Automatic Lambda trigger on upload

---

## Impact

- Unauthorized file uploads
- Backend Lambda execution triggered by attackers
- Potential injection or replacement of receipt files
- Violation of data and execution boundaries

---

## Root Cause

- S3 bucket misconfiguration
- Public ACL + policy allowed uploads
- No restriction on who can upload files
- Lambda triggered on any object creation

---

## Fix

- Enable **Block all public access**
- Restrict S3 write permissions to specific IAM roles
- (Optional) Validate uploads inside Lambda

---

## Result

- Unauthorized uploads blocked
- Lambda no longer triggered by attackers
- System secured

---


