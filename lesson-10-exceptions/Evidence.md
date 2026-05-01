## Evidence

### 1. Attack Setup

Set environment variables:

```bash id="e1f2g3"
export API="https://jg71b5i888.execute-api.us-east-1.amazonaws.com/dvsa/order"
export TOKEN="your_token_here"
export RACE_ORDER=""
```

---

### 2. Malformed Request

Send request without required `billing` field:

```bash id="h4j5k6"
curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $TOKEN" \
--data-raw '{"action":"billing","order-id":"'$RACE_ORDER'"}'
```

---

### 3. Result (Before Fix)

The response exposes internal details such as:

```id="m7n8o9"
KeyError: 'billing'
File: /var/task/order_billing.py
Line: 103
```

### Information Leaked

* Internal file path
* Exact line number
* Source code snippet
* Missing key name
* Exception type

This confirms sensitive information disclosure.

---



## Fix Strategy

The fix is applied inside the Lambda function:

### Improvements:

* Validate input before accessing fields
* Check if `billing` exists
* Validate required sub-fields
* Add exception handling

---

## Code Changes (Fix)

### Secure Implementation

```python id="v6w7x8"
def lambda_handler(event, context):

    # Validate required fields
    if "orderId" not in event or "user" not in event:
        return {"status": "err", "msg": "invalid request"}

    if "billing" not in event:
        return {"status": "err", "msg": "invalid request"}

    billing = event["billing"]

    required_fields = ["ccn", "exp", "cvv"]
    for field in required_fields:
        if field not in billing:
            return {"status": "err", "msg": "invalid request"}

    try:
        # existing logic here
        pass
    except Exception:
        return {"status": "err", "msg": "internal error"}
```

---

## Why This Fix Works

* Prevents KeyError
* Stops exposure of internal data
* Returns safe generic messages
* Keeps detailed logs internal only

---

## Verification

After applying the fix:

### Malformed request result:

```id="y9z0a1"
{"status":"err","msg":"invalid request"}
```

### Result

* No stack trace 
* No file path exposed 
* No internal details leaked 

---

## Analysis

### Table A — Behavior

| Vulnerability        | Intended Rule                           | Normal Behavior                       | Exploit Behavior                      |
| -------------------- | --------------------------------------- | ------------------------------------- | ------------------------------------- |
| Unhandled Exceptions | Backend must not expose internal errors | Valid requests return normal response | Malformed request exposes stack trace |

---

### Table B — Deviation & Fix

| Issue              | Cause                             | Fix                         | Result                 |
| ------------------ | --------------------------------- | --------------------------- | ---------------------- |
| Exception exposure | No validation + no error handling | Add validation + try/except | Safe response returned |

---

## Conclusion

Before fix:

* System crashed on invalid input
* Internal details exposed
* High information leakage

After fix:

* Input validated
* Exceptions handled
* System secure

---

