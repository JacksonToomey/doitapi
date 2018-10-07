from unittest.mock import MagicMock
from auth import AuthProviderComponent


def test_login(client, mock_provider_factory):
    m = MagicMock(
        get_user_from_token=lambda x: {
            'id': 'fakeid',
            'email': 'fake'
        },
        get_user_token=lambda x: 'some.fake.token'
    )
    mock_auth_provider = mock_provider_factory(AuthProviderComponent)
    mock_auth_provider.set_mock(m)
    resp = client.post('/login', json={'token': 'sometoken'})
    assert resp.status_code == 200
