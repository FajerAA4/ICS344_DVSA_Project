# DVSA-ADMIN-GET-RECEIPT — lambda_function.py (PATCHED)

# Change from the vulnerable version: an authorization check is performed
import boto3

def lambda_handler(event, context):
    # ===== Authorization check =====
    is_admin = event.get("isAdmin")

    if is_admin is not True and is_admin != "true":
        return {
            "status": "error",
            "message": "Unauthorized - Admin access required"
        }

    client   = boto3.client('s3')
    resource = boto3.resource('s3')

    m = ""
    d = ""
    y = event["year"]

    if "month" in event:
        m = event["month"] + "/"
        if "day" in event:
            d = event["day"] + "/"

    prefix = "{}/{}{}".format(y, m, d)

