from inspect import Parameter

import requests


class RequestSessionComponent:
    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is requests.Session

    def resolve(self) -> requests.Session:
        return requests.Session()
