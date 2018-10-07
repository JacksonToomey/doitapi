from unittest.mock import MagicMock

import pytest
from molten import testing, Settings, SettingsComponent
from molten.contrib.sqlalchemy import SQLAlchemyEngineComponent,\
    SQLAlchemySessionComponent
from auth import AuthProviderComponent

from factory import create_app


class MockProvider:
    def __init__(self, component):
        self.component_mock = component
        self.mock = None

    def set_mock(self, mock):
        self.mock = mock

    def clear_mock(self):
        self.mock = None

    def can_handle_parameter(self, parameter):
        return self.component_mock().can_handle_parameter(parameter)

    def resolve(self):
        if self.mock:
            return self.mock

        return MagicMock()


@pytest.fixture(scope='session')
def test_app():
    settings = Settings({
        'database_engine_dsn': 'sqlite://',
        'identity_server': 'http://localhost',
        'secret_key': 'fake_secret',
    })
    app = create_app(
        settings=settings,
        components=[
            SettingsComponent(settings),
            SQLAlchemyEngineComponent(),
            SQLAlchemySessionComponent(),
            # RequestSessionComponent(),
            MockProvider(AuthProviderComponent),
        ],
    )
    yield app


@pytest.fixture(scope='session')
def client(test_app):
    return testing.TestClient(test_app)


@pytest.fixture
def mock_provider_factory(test_app):
    def get_mock(component_type):
        for component in test_app.injector.components:
            if getattr(component, 'component_mock', None) is component_type:
                return component
    yield get_mock


@pytest.fixture(autouse=True)
def clear_mocks(test_app):
    yield
    for component in test_app.injector.components:
        if isinstance(component, MockProvider):
            component.clear_mock()
