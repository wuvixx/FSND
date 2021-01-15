import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'unta.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'shop'

# AuthError Exception


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({
            'code': 'bad_header',
            'description': 'Missing authorization header'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'missing_bearer',
            'description': 'Authorization must start with a bearer'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'bad_header',
            'description': 'Invalid header'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    if not permission:
        return True

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permissions not found.'
        }, 403)

    return True


def verify_decode_jwt(token):
    url = urlopen('https://' + AUTH0_DOMAIN + '/.well-known/jwks.json')
    known_jwks = json.loads(url.read())
    this_token_header = jwt.get_unverified_header(token)
    this_key = {}
    for key in known_jwks['keys']:
        if key['kid'] == this_token_header['kid']:
            this_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    payload = None
    if this_key:
        try:
            payload = jwt.decode(
                token, this_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE)
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'expired_token',
                'description': 'Token expired'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Invalid claims'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'bad_request',
                'description': 'Misformatted request'
            }, 401)

        if payload:
            return payload


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
