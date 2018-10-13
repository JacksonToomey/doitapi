from molten import Route


def get_upcoming() -> list:
    return [
        {
            'id': 2,
            'name': 'Test Chore 2',
            'dueDate': '2018-10-14',
            'details': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum'
        },
        {
            'id': 1,
            'name': 'Test Chore 1',
            'dueDate': '2018-10-20',
            'details': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum'
        }
    ]


def complete_upcoming(chore_id: str) -> dict:
    return {}


routes = [
    Route('/upcoming', get_upcoming, method='GET', name='get-upcoming'),
    Route('/upcoming/{chore_id}', get_upcoming, method='POST', name='get-upcoming'),
]
