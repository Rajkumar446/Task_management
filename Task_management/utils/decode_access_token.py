from auth.jwt_handler import verify_access_token

def decode_access_token(token: str):
    return verify_access_token(token)
