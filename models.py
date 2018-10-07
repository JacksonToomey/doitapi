from inspect import Parameter

from sqlalchemy.ext.declarative import declarative_base
from molten.contrib.sqlalchemy import Session


Model = declarative_base()


class Manager:
    def __init__(self, session: Session):
        self.session = session


class ManagerComponent:
    def __init__(self, manager_type: Manager):
        self.manager_type = manager_type

    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is self.manager_type

    def resolve(self, session: Session) -> Manager:
        return self.manager_type(session)
