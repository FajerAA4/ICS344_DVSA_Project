# DVSA-ADMIN-UPDATE-ORDERS — patched lambda_function.py (relevant block only)
#
# This file is a snippet showing where the access-control check was inserted
# inside the existing handler. Drop the highlighted block in immediately
# after the JWT is decoded into `token`, and BEFORE any DynamoDB update
# logic runs.

def lambda_handler(event, context):
    # ... existing JWT extraction and decoding produces `token` (a dict
    # of decoded claims) ...

    # =========================================================
    # FIX: Added admin-only authorization check to prevent
    # unauthorized access to order update functionality
    # =========================================================
    scope = token.get("scope", "")

    if "admin" not in scope.lower():
        return {
            "status": "err",
            "msg": "Unauthorized. Admin access required."
        }
    # =========================================================

    # ... existing order-update logic (DynamoDB UpdateItem etc.) continues
    # below unchanged ...
    return {"status": "ok", "msg": "order updated"}
