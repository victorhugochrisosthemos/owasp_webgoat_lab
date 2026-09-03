import base64
import json

token = "TOKEN_JWT"

payload = token.split(".")[1]
payload += "=" * (-len(payload) % 4)

dados = base64.urlsafe_b64decode(payload)

print(json.dumps(json.loads(dados), indent=2))
