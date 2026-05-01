## Evidence

### 1. Vulnerability Description

The system processes billing without locking the order.

This allows:

* Billing request (calculates price)
* Update request (changes cart)

 Both execute at the same time

---

### 2. Attack Scenario

Two concurrent requests are sent:

1. Billing request
2. Update request

### Result

```
Paid for: 1 item  
Received: 8 items
```

 Confirms race condition exploitation

---

### 3. Code Behavior (Before Fix)

The system only checks:

```
if status < 120
```

Without:

* Locking
* Concurrency control

---

### 4. Fix Strategy

The fix is implemented in the Lambda function:

* Add atomic locking using DynamoDB
* Use `ConditionExpression`
* Lock order before processing begins

---

### 5. Code Changes (Fix)

Location:
DVSA-ORDER-BILLING → order_billing.py

```python
if status < 120:
    # FIX: Lock the order before processing
    try:
        table.update_item(
            Key={"orderId": orderId, "userId": userId},
            UpdateExpression="SET orderStatus = :lockstatus",
            ConditionExpression="orderStatus = :currentstatus",
            ExpressionAttributeValues={
                ":lockstatus": Decimal(200),
                ":currentstatus": Decimal(status)
            }
        )
    except Exception as e:
        res = {"status": "err", "msg": "order already being processed"}
        return res
```

---

### 6. Why This Fix Works

* Uses DynamoDB **ConditionExpression**
* Ensures atomic update
* Only one request can modify the order

 Prevents race conditions completely

---

### 7. Verification (After Fix)

After applying the fix and repeating the attack:

```
{"status":"err","msg":"order already being processed"}
```

### Result

* Update request blocked 
* Billing proceeds safely 
* Order remains consistent

---

## Analysis

### Table A — Behavior

| Vulnerability       | Intended Rule                       | Normal Behavior                    | Exploit Behavior                |
| ------------------- | ----------------------------------- | ---------------------------------- | ------------------------------- |
| Logic Vulnerability | Order must be locked during billing | Correct price for correct quantity | Quantity changed during payment |

---

### Table B — Deviation & Fix

| Issue          | Cause      | Fix                     | Result                     |
| -------------- | ---------- | ----------------------- | -------------------------- |
| Race Condition | No locking | Add ConditionExpression | Concurrent updates blocked |

---

## Conclusion

Before fix:

* No order locking
* Race condition possible
* Incorrect billing

After fix:

* Order locked
* No concurrent updates
* System consistent

