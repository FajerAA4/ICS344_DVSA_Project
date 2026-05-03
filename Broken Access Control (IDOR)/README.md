# Additional Vulnerability -- Broken Access Control (IDOR)

## 1- Goal and Vulnerability Summary:

This vulnerability demonstrates a Broken Access Control flaw combined with an Insecure Direct Object Reference (IDOR) in the DVSA order management system. The system allows users to modify orders belonging to other users without verifying ownership, leading to unauthorized access and modification of sensitive data.

---

## 2- Root Cause:

The vulnerability exists because the application does not validate whether the authenticated user owns the requested order. The system directly accepts the order-id provided in the request without checking if it belongs to the current user.

---

## 3- Setup

• Application: DVSA
• Service: AWS Lambda + API Gateway
• Database: DynamoDB (DVSA-ORDERS-DB)
• Endpoint used: /dvsa/order
• Tool: Git Bash (curl)

---

## 4- Steps

1. Create two users:
   a. User A (attacker)
   b. User B (victim)

2. From User B:
   a. Create an order
   b. Copy the order-id

3. From User A:
   a. Extract JWT token from browser DevTools

4. Send the request using User A token

---

## 5- Evidence:

The screenshots show that a request was sent using a token from one user while modifying an order belonging to another user. The system returned “cart updated”, confirming that the update was accepted.The DynamoDB record also shows that the item quantity was changed to 5, even though the userId belongs to a different user.

---

## 6- Fix Strategy

The fix is to enforce strict ownership validation before allowing access or modification of any order.The system must verify that:

order.userId == authenticatedUserId

If not, the request must be rejected.

---



---

##  Tables Analysis Tables

### Table A: Behavior Analysis

| Vulnerability                | Intended Rule(s)                         | Artifacts Used to Infer Rule | Normal Behavior Evidence               | Exploit Behavior Evidence                                               |
| ---------------------------- | ---------------------------------------- | ---------------------------- | -------------------------------------- | ----------------------------------------------------------------------- |
| Broken Access Control / IDOR | Users must only access their own orders. | API response, DynamoDB data  | Users can modify their own orders only | Malformed request caused KeyError and exposed stack trace and file path |

---

### Table B: Deviation and Remediation

| Vulnerability                | Why This Is a Deviation                                | Deviation Class          | Fix Applied (Where)                              | Post-Fix Verification            |
| ---------------------------- | ------------------------------------------------------ | ------------------------ | ------------------------------------------------ | -------------------------------- |
| Broken Access Control / IDOR | System allows unauthorized access to other users' data | Security-relevant misuse | Input validation added in admin_update_orders.py | Unauthorized request is rejected |

---

##  Takeaway:

The DVSA order management system contained a Broken Access Control (IDOR) vulnerability that allowed authenticated users to modify orders belonging to other users. The root cause was the absence of ownership validation in the updateItem function — the system accepted any order-id without verifying it belonged to the requesting user. The fix was implemented by adding a get_item check in DynamoDB before processing any update, ensuring the userId in the order matches the authenticated user extracted from the JWT token. Post-fix verification confirmed that unauthorized requests are now rejected with an unauthorized response, preventing cross-user data manipulation.

---


