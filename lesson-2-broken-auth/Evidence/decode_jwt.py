import base64
import json
import os

def decode_token(token):
    try:
        payload = token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded)
    except Exception as e:
        return {"error": str(e)}

TOKEN_B = os.getenv("TOKEN_B")
TOKEN_C = os.getenv("TOKEN_C")

for name, token in [("TOKEN_B", TOKEN_B), ("TOKEN_C", TOKEN_C)]:
    print(f"\n{name}:")
    data = decode_token(token)
    print("username:", data.get("username"))
    print("sub:", data.get("sub"))
