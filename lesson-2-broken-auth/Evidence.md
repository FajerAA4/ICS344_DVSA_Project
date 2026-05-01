# Evidence

This folder contains proof of the Broken Authentication vulnerability.

## Files

- 01_devtools_request.png → API request capture
- 02_jwt_decode_script.png → JWT decoding script output
- 03_normal_behavior.png → Normal behavior (User B only)
- 04_forged_token_exploit.png → Exploit showing unauthorized access
- 05_order_details.png → Full victim data exposure

## Notes

These screenshots demonstrate that modifying JWT payload allows impersonation.
