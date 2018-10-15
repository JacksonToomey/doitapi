import enum
from uuid import uuid4
from inspect import Parameter
from typing import List

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


def get_id():
    return uuid4().hex.upper()


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
        default=get_id,
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

    @classmethod
    def from_definition(cls, chore_definition: ChoreDefinition, due_date: pendulum.DateTime):
        return cls(
            name=chore_definition.name,
            details=chore_definition.details,
            owner_id=chore_definition.owner_id,
            chore_definition_id=chore_definition.id,
            due_date=due_date,
        )


class UserProvider:
    def __init__(self, session: Session):
        self.session = session
        self._user = None

    def load_user(self, user_id: str):
        self._user = self.session.query(User).get(user_id)

    def get_user(self) -> User:
        return self._user

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


class Manager:
    def __init__(self, session: Session, user_provider: UserProvider):
        self.session = session
        self.user_provider = user_provider


class ChoreInstanceManager(Manager):

    def get_upcoming_chores(self) -> List[ChoreInstance]:
        user = self.user_provider.get_user()
        return self.session.query(ChoreInstance)\
            .filter_by(completed=False)\
            .filter_by(owner_id=user.id)\
            .filter(ChoreInstance.due_date <= pendulum.now('UTC').add(days=14))\
            .order_by(ChoreInstance.due_date.asc())\
            .all()

    def complete_chore(self, chore_id: str):
        instance = self.session.query(ChoreInstance).get(chore_id)
        if instance is None:
            return

        chore_definition = self.session.query(ChoreDefinition).get(instance.chore_definition_id)

        instance.completed = True
        self.session.add(instance)
        amount = chore_definition.frequency_amount
        frequency_type = chore_definition.frequency_type.value

        date_kwargs = {
            frequency_type: amount,
        }
        new_due_date = pendulum.now('UTC').add(**date_kwargs)
        new_instance = ChoreInstance.from_definition(chore_definition, new_due_date)
        self.session.add(new_instance)
        self.session.flush()


class ChoreDefinitionManager(Manager):
    def persist_chore(self, chore_data) -> ChoreDefinition:
        user = self.user_provider.get_user()
        chore_definition = ChoreDefinition(
            name=chore_data.name,
            details=chore_data.details,
            frequency_amount=chore_data.frequency_amount,
            frequency_type=chore_data.frequency_type,
            owner_id=user.id,
            id=get_id(),
        )
        self.session.add(chore_definition)
        self.session.add(ChoreInstance.from_definition(chore_definition, chore_data.start_date))
        self.session.flush()
        return chore_definition


class ManagerComponent:
    def __init__(self, manager_type: Manager):
        self.manager_type = manager_type

    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is self.manager_type

    def resolve(self, session: Session, user_provider: UserProvider) -> Manager:
        return self.manager_type(session, user_provider)


class UserProviderComponent:
    def can_handle_parameter(self, parameter: Parameter) -> bool:
        return parameter.annotation is UserProvider

    def resolve(self, session: Session) -> Manager:
        return UserProvider(session)
