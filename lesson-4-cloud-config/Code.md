# Evidence – Lesson 4 (Insecure Cloud Configuration)

---

## 1. Misconfiguration

The S3 bucket had:

- Block all public access:  OFF

This allowed any user to upload files without authentication.

---

## 2. Environment Setup

- AWS Region: us-east-1
- Bucket: dvsa-receipts-bucket-898322960732-us-east-1
- Lambda: DVSA-SEND-RECEIPT-EMAIL
- Tools: AWS Console, CloudShell, CloudWatch

---

## 3. Attack (Unauthorized Upload)

Command used:

```bash
echo "test file content" > /tmp/payload.txt

aws s3 cp /tmp/payload.txt \
s3://dvsa-receipts-bucket-898322960732-us-east-1/attacker/payload.txt \
--acl public-read
