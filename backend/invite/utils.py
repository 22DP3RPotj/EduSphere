import secrets


INVITE_TOKEN_LENGTH = 12


def generate_token() -> str:
    return secrets.token_urlsafe(INVITE_TOKEN_LENGTH)[:INVITE_TOKEN_LENGTH]
