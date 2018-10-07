import json
from inspect import Parameter
from typing import Any, Callable, Optional

import requests
from molten import schema, Settings, HTTP_401, Response, HTTP_200, Cookie


def auth_middleware(handler: Callable[..., Any]) -> Callable[..., Any]:
    def middleware() -> Any:
        # TODO: auth check
        if getattr(handler, 'exclude_auth', False):
            return handler()

        return handler()

    return middleware


class AuthProvider:
    def __init__(self, session: requests.Session, identity_host: str):
        self.session = session
        self.host = identity_host

    def get_user_from_token(self, token: str) -> Optional[dict]:
        # TODO:  actualy get identity
        # url = f'{self.host}/.netlify/identity/user'
        # resp = self.session.get(url, headers={
        #     'Authorization': f'Bearer {token}'
        # })

        # if resp.status_code != 200:
        #     return None

        # data = resp.json()
        # return data
        return {
            'id': 'someid',
            'email': 'some@email.com'
        }

    def get_user_token(self, user: dict) -> str:
        return 'some.fake.token'


class AuthProviderComponent:
    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is AuthProvider

    def resolve(self, session: requests.Session, settings: Settings) -> AuthProvider:
        return AuthProvider(session, settings['identity_server'])


def exclude_auth(f):
    f.exclude_auth = True
    return f


@schema
class Login:
    token: str


@exclude_auth
def login(login: Login, auth: AuthProvider) -> Response:
    user = auth.get_user_from_token(login.token)
    if user is None:
        return Response(HTTP_401, content='{}')

    token = auth.get_user_token(user)

    return Response(
        HTTP_200,
        content=json.dumps({'token': token}),
        headers={
            'Content-Type': 'application/json',
        },
    )
