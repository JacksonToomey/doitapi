import pendulum
from typing import Optional, Union

from molten import Route, schema, field

from models import ChoreInstanceManager,\
    FrequencyTypes,\
    ChoreDefinitionManager
from auth import AuthProvider
from validators import PendulumValidator


@schema
class Chore:
    id: Optional[str] = field(response_only=True)
    name: str
    details: str
    frequency_type: FrequencyTypes = field(allow_coerce=True, request_name='frequencyType', response_name='frequencyType')
    frequency_amount: int = field(minimum=1, request_name='frequencyAmount', response_name='frequencyAmount')
    start_date: Union[str, pendulum.DateTime] = field(request_only=True, validator=PendulumValidator, request_name='startDate', response_name='startDate')


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


def get_chore(chore_id: str) -> dict:
    return {}


def get_chores() -> list:
    return []


def create_chore(chore: Chore, chore_manager: ChoreDefinitionManager) -> Chore:
    chore_model = chore_manager.persist_chore(chore)

    return Chore(
        id=chore_model.id,
        name=chore_model.name,
        details=chore_model.details,
        frequency_type=str(chore_model.frequency_type),
        frequency_amount=chore_model.frequency_amount,
        start_date=None,
    )


def update_chore() -> dict:
    return {}


def delete_chore() -> str:
    return ''


routes = [
    Route('/upcoming', get_upcoming, method='GET', name='get-upcoming'),
    Route('/upcoming/{chore_id}', complete_upcoming, method='POST', name='complete-upcoming'),
    Route('/chores', get_chores, method='GET', name='get-chores'),
    Route('/chores', create_chore, method='POST', name='create-chore'),
    Route('/chores/{chore_id}', get_chore, method='GET', name='get-chore'),
    Route('/chores/{chore_id}', get_chore, method='POST', name='update-chore'),
    Route('/chores/{chore_id}', delete_chore, method='DELETE', name='delete-chore'),
]
