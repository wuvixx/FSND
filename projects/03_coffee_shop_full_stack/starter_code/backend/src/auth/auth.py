import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'unta.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
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

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
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

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
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
            payload = jwt.decode(token, this_key, algorithms=ALGORITHMS, audience=API_AUDIENCE)
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

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
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