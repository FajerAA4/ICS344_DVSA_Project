# Evidence

##  Exploit Request (Before Fix)

```bash
echo" curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $TOKEN" \
--data-raw '{"action":"update","order-id":"'$OTHER_ORDER'","items":{"1017":5}}'
```

Expected result (vulnerable system):

```json
{
  "status": "ok",
  "msg": "cart updated"
}
```

---

##  Fixed Code (Ownership Validation)

```python
order_id = event["order-id"]
authenticated_user_id = event["user"]

order = table.get_item(
    Key={
        "orderId": order_id
    }
)

if "Item" not in order:
    return {
        "status": "err",
        "msg": "order not found"
    }

if order["Item"]["userId"] != authenticated_user_id:
    return {
        "status": "err",
        "msg": "unauthorized"
    }

table.update_item(
    Key={
        "orderId": order_id
    },
    UpdateExpression="SET items = :items",
    ExpressionAttributeValues={
        ":items": event["items"]
    }
)

return {
    "status": "ok",
    "msg": "cart updated"
}
```

---

##  Verification Request (After Fix)

```bash
echo" curl -s "$API" \
-H "content-type: application/json" \
-H "authorization: $TOKEN" \
--data-raw '{"action":"update","order-id":"'$OTHER_ORDER'","items":{"1017":5}}'
```

Expected result (after fix):

```json
{
  "status": "err",
  "msg": "unauthorized"
}
```
