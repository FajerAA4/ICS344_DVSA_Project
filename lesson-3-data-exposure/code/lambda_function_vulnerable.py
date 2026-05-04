# DVSA-ADMIN-GET-RECEIPT — lambda_function.py (VULNERABLE — DO NOT DEPLOY)
#
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
