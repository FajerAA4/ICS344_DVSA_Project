# DVSA-ADMIN-GET-RECEIPT — lambda_function.py (VULNERABLE — DO NOT DEPLOY)
#
# This snippet shows the top of the original handler. The function jumps
# straight from "I got an event" to "let me build an S3 client and start
# listing objects" with NO authorization check anywhere. Any caller who
# can invoke the Lambda gets back a signed URL.

import boto3

def lambda_handler(event, context):
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

    # ... continues to list objects from the receipts bucket using `prefix`,
    # zip them up, upload the ZIP back to S3, and return a pre-signed URL.
