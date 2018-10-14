import enum
from uuid import uuid4
from inspect import Parameter

import pendulum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import types,\
    Column,\
    String,\
    Text,\
    ForeignKey,\
    Integer,\
    CheckConstraint,\
    Enum,\
    Boolean
from molten.contrib.sqlalchemy import Session


class PendulumDateTime(types.TypeDecorator):
    impl = types.DateTime

    def process_result_value(self, value, dialect):
        return pendulum.instance(value)


class FrequencyTypes(enum.Enum):
    DAYS = 'days'
    WEEKS = 'weeks'
    MONTHS = 'months'
    YEARS = 'years'


Model = declarative_base()


class Base(Model):
    __abstract__ = True
    id = Column(
        String(32),
        nullable=False,
        primary_key=True,
        default=lambda: uuid4().hex.upper(),
    )
    created_at = Column(
        PendulumDateTime(timezone=True),
        nullable=False,
        default=lambda: pendulum.now('UTC'),
    )
    updated_at = Column(
        PendulumDateTime(timezone=True),
        nullable=False,
        default=lambda: pendulum.now('UTC'),
        onupdate=lambda: pendulum.now('UTC'),
    )


class User(Base):
    __tablename__ = 'user'
    external_id = Column(String(36), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)


class ChoreDefinition(Base):
    __tablename__ = 'chore_definition'

    name = Column(String(255), nullable=False)
    owner_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    details = Column(Text, nullable=False, default='')
    frequency_amount = Column(Integer, nullable=False)
    frequency_type = Column(Enum(FrequencyTypes), nullable=False)

    __table_args = (
        CheckConstraint(frequency_amount >= 0, name='check_frequency_amount_positive'),
    )


class ChoreInstance(Base):
    __tablename__ = 'chore_instance'

    name = Column(String(255), nullable=False)
    details = Column(Text, nullable=False, default='')
    owner_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    chore_definition_id = Column(ForeignKey('chore_definition.id', ondelete='CASCADE'), nullable=False)
    due_date = Column(PendulumDateTime(timezone=True), nullable=False, default=lambda: pendulum.now('UTC'))
    completed = Column(Boolean, nullable=False, default=False)


class Manager:
    def __init__(self, session: Session):
        self.session = session


class UserManager(Manager):
    def get_user_from_external(self, user: dict) -> User:
        try:
            user = self.session.query(User)\
                .filter_by(external_id=user['id'])\
                .filter_by(email=user['email'])\
                .one()
            return user
        except NoResultFound:
            user = User(
                external_id=user['id'],
                email=user['email'],
            )
            self.session.add(user)
            self.session.flush()
            return user


class ManagerComponent:
    def __init__(self, manager_type: Manager):
        self.manager_type = manager_type

    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is self.manager_type

    def resolve(self, session: Session) -> Manager:
        return self.manager_type(session)
