import json
from flask import request, _request_ctx_stack, Flask, abort, jsonify
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from config import auth_config

AUTH0_DOMAIN = auth_config['AUTH0_DOMAIN']
ALGORITHMS = auth_config['ALGORITHMS']
API_AUDIENCE = auth_config['API_AUDIENCE']

# Authorization Error
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Authorization Header
def get_token_auth_header():
    auth_header = request.headers.get('Authorization',None)
    #it will raise error if authorization is missing in header
    head_parts = auth_header.split()

    if not auth_header:
        print('not auth')
        raise AuthError({
            'code': 'authorization header_missing',
            'description': 'Authorizaion header is missing'}, 401)


    if  head_parts[0].lower() != 'bearer':
        # checking if bearer is present in authorization
        print('no bearer')
        raise AuthError({
            'code': 'invalid header',
            'description': 'Authorization header must have a bearer'
        }, 401)

    elif len(head_parts) == 1:
        # throws error if token is missing in authorizatio(i.e, bearer is only present)
        print('no token')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
# error is raised if authorization has more components than bearer and token
    elif len(head_parts) > 2:
        raise AuthError({
            'code': 'invalid header',
            'description': 'Authorization header must be bearer token'
        }, 401)

    return head_parts[1]


def check_permissions(permission, payload):
    # This functions check the permissions that are in the JWT
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check'
                        + ' the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)



def requires_auth(permissions=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                print('could not verify_decode_jwt')
                abort(401)

            check_permissions(permissions, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator