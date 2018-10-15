import json
from inspect import Parameter
from typing import Any, Callable, Optional

import requests
from jose import jwt
from molten import schema, Settings, HTTP_401, HTTP_403, Response, HTTP_200, Header
from models import UserProvider, User


def auth_middleware(handler: Callable[..., Any]) -> Callable[..., Any]:
    def middleware(authorization: Optional[Header], auth_provider: AuthProvider, user_provider: UserProvider) -> Any:
        if getattr(handler, 'exclude_auth', False):
            return handler()

        if not authorization:
            return Response(HTTP_403, content='{}')

        if not authorization.startswith('Bearer '):
            return Response(HTTP_403, content='{}')

        token = authorization.split(' ')[1]

        if not token:
            return Response(HTTP_403, content='{}')

        # TODO: verify token
        user_provider.load_user('9B883A9EAD2346D4B86DFD27293BBA54')
        return handler()

    return middleware


class AuthProvider:
    def __init__(self, session: requests.Session, identity_host: str, secret_key: str):
        self.session = session
        self.host = identity_host
        self.secret_key = secret_key

    def get_user_from_token(self, token: str) -> Optional[dict]:
        url = f'{self.host}/.netlify/identity/user'
        resp = self.session.get(url, headers={
            'Authorization': f'Bearer {token}'
        })

        if resp.status_code != 200:
            return None

        data = resp.json()
        return data

    def get_user_token(self, user: User) -> str:
        token = jwt.encode({
            'id': user.id,
            'email': user.email,
        }, self.secret_key, algorithm='HS256')
        return token


class AuthProviderComponent:
    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is AuthProvider

    def resolve(self, session: requests.Session, settings: Settings) -> AuthProvider:
        return AuthProvider(session, settings['identity_server'], settings['secret_key'])


def exclude_auth(f):
    f.exclude_auth = True
    return f


@schema
class Login:
    token: str


@exclude_auth
def login(login: Login, auth: AuthProvider, user_manager: UserProvider) -> Response:
    user = auth.get_user_from_token(login.token)
    if user is None:
        return Response(HTTP_401, content='{}')

    user = user_manager.get_user_from_external(user)

    token = auth.get_user_token(user)

    return Response(
        HTTP_200,
        content=json.dumps({'token': token}),
        headers={
            'Content-Type': 'application/json',
        },
    )
