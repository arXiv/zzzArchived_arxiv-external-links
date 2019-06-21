"""Web Server Gateway Interface entry-point for the user interface."""

from relations.factory import create_ui_app
import os


__flask_app__ = create_ui_app()


def application(environ, start_response):
    """WSGI application factory."""
    for key, value in environ.items():
        if type(value) is str:
            os.environ[key] = value
            if key in __flask_app__.config:
                __flask_app__.config[key] = value
    return __flask_app__(environ, start_response)
