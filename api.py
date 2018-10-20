import pendulum
from typing import Optional, Union, TypeVar, Type

from molten import Route, schema, field, HTTP_404

from models import ChoreInstanceManager,\
    FrequencyTypes,\
    ChoreDefinitionManager,\
    ChoreDefinition
from auth import AuthProvider
from validators import PendulumValidator


T = TypeVar('T', bound='Chore')


@schema
class Chore:
    id: Optional[str] = field(response_only=True)
    name: str
    details: str
    frequency_type: FrequencyTypes = field(
        allow_coerce=True,
        request_name='frequencyType',
        response_name='frequencyType',
    )
    frequency_amount: int = field(
        minimum=1,
        request_name='frequencyAmount',
        response_name='frequencyAmount',
    )
    start_date: Union[str, pendulum.DateTime] = field(
        request_only=True,
        validator=PendulumValidator,
        request_name='startDate',
        response_name='startDate',
    )

    @classmethod
    def from_chore_model(cls: Type[T], chore_model: ChoreDefinition) -> T:
        return cls(
            id=chore_model.id,
            name=chore_model.name,
            details=chore_model.details,
            frequency_type=chore_model.frequency_type.value,
            frequency_amount=chore_model.frequency_amount,
            start_date=None,
        )


def get_upcoming(chore_instance_manager: ChoreInstanceManager, auth_provider: AuthProvider) -> list:
    upcoming_chores = chore_instance_manager.get_upcoming_chores()
    return [{
        'id': upcoming_chore.id,
        'name': upcoming_chore.name,
        'dueDate': str(upcoming_chore.due_date),
        'details': upcoming_chore.details
    } for upcoming_chore in upcoming_chores]


def complete_upcoming(chore_id: str, chore_instance_manager: ChoreInstanceManager) -> dict:
    chore_instance_manager.complete_chore(chore_id)
    return {}


def get_chore(chore_id: str, chore_manager: ChoreDefinitionManager) -> dict:
    chore_model = chore_manager.get_chore(chore_id)
    if not chore_model:
        return HTTP_404, 'not found'
    return Chore.from_chore_model(chore_model)


def get_chores(chore_manager: ChoreDefinitionManager) -> Chore:
    chores = chore_manager.get_chores()
    return [Chore.from_chore_model(chore_model) for chore_model in chores]


def create_chore(chore: Chore, chore_manager: ChoreDefinitionManager) -> Chore:
    chore_model = chore_manager.persist_chore(chore)
    return Chore.from_chore_model(chore_model)


def delete_chore(chore_id: str, chore_manager: ChoreDefinitionManager) -> str:
    chore_manager.delete_chore(chore_id)
    return ''


routes = [
    Route('/upcoming', get_upcoming, method='GET', name='get-upcoming'),
    Route('/upcoming/{chore_id}', complete_upcoming, method='POST', name='complete-upcoming'),
    Route('/chores', get_chores, method='GET', name='get-chores'),
    Route('/chores', create_chore, method='POST', name='create-chore'),
    Route('/chores/{chore_id}', get_chore, method='GET', name='get-chore'),
    Route('/chores/{chore_id}', delete_chore, method='DELETE', name='delete-chore'),
]
