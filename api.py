from molten import Route


def get_upcoming() -> list:
    return []


def complete_upcoming(chore_id: str) -> dict:
    return {}


def get_chore(chore_id: str) -> dict:
    return {}


def get_chores() -> list:
    return []


def create_chore() -> dict:
    return {}


def update_chore() -> dict:
    return {}


def delete_chore() -> str:
    return ''


routes = [
    Route('/upcoming', get_upcoming, method='GET', name='get-upcoming'),
    Route('/upcoming/{chore_id}', get_upcoming, method='POST', name='get-upcoming'),
    Route('/chores', get_chores, method='GET', name='get-chores'),
    Route('/chores', create_chore, method='POST', name='create-chore'),
    Route('/chores/{chore_id}', get_chore, method='GET', name='get-chore'),
    Route('/chores/{chore_id}', get_chore, method='POST', name='update-chore'),
    Route('/chores/{chore_id}', delete_chore, method='DELETE', name='delete-chore'),
]
