import requests
from jose import jwt
from fastapi import Request, HTTPException

CLERK_ISSUER = "https://darling-beagle-63.clerk.accounts.dev"
CLERK_JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"

jwks = requests.get(CLERK_JWKS_URL).json()

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth.replace("Bearer ", "")

    header = jwt.get_unverified_header(token)
    key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])

    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience="authenticated",
        issuer=CLERK_ISSUER
    )

    return payload["sub"]  # ✅ Clerk user ID
