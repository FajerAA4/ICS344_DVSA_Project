# DVSA-ADMIN-UPDATE-ORDERS — patched lambda_function.py (relevant block only)

def lambda_handler(event, context):
    # FIX: Added admin-only authorization check to prevent
    # unauthorized access to order update functionality
    scope = token.get("scope", "")

    if "admin" not in scope.lower():
        return {
            "status": "err",
            "msg": "Unauthorized. Admin access required."
        }

    return {"status": "ok", "msg": "order updated"}
