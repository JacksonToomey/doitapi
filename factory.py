import os

from dotenv import load_dotenv
from molten.contrib.sqlalchemy import SQLAlchemyEngineComponent,\
    SQLAlchemyMiddleware,\
    SQLAlchemySessionComponent
from molten import App,\
    Route,\
    Include,\
    ResponseRendererMiddleware,\
    Settings,\
    SettingsComponent

from api import routes
from session import RequestSessionComponent
from models import ManagerComponent,\
    ChoreInstanceManager,\
    ChoreDefinitionManager,\
    UserProviderComponent
from auth import auth_middleware, login, AuthProviderComponent


load_dotenv()


def create_app(middleware=None, components=None, settings=None):
    if settings is None:
        settings = Settings({
            'database_engine_dsn': os.environ['SQLALCHEMY_URI'],
            'identity_server': os.environ['IDENTITY_SERVER'],
            'secret_key': os.environ['SECRET_KEY'],
        })

    if middleware is None:
        middleware = [
            ResponseRendererMiddleware(),
            SQLAlchemyMiddleware(),
            auth_middleware,
        ]

    if components is None:
        components = [
            SettingsComponent(settings),
            SQLAlchemyEngineComponent(),
            SQLAlchemySessionComponent(),
            RequestSessionComponent(),
            AuthProviderComponent(),
            ManagerComponent(ChoreInstanceManager),
            ManagerComponent(ChoreDefinitionManager),
            UserProviderComponent(),
        ]

    app = App(
        routes=[
            Route('/login', login, method='POST', name='login'),
            Include(
                '/api',
                routes,
                namespace='api',
            )
        ],
        middleware=middleware,
        components=components,
    )
    return app
