"""
Request controllers for the external links service.

These may be used handle requests originating from the :mod:`.routes.api` and/or the
:mod:`.routes.ui`.

If the behavior of these controllers diverges along the UI/API lines, then we can split this
into ``controllers/api.py`` and ``controllers/ui.py``.
"""

from typing import Tuple, Any, Dict
from http import HTTPStatus

from werkzeug.datastructures import MultiDict

Response = Tuple[Dict[str, Any], HTTPStatus, Dict[str, str]]


def service_status(params: MultiDict) -> Response:
    """
    Handle requests for the service status endpoint.

    Returns ``200 OK`` if the service is up and ready to handle requests.
    """
    return {'iam': 'ok'}, HTTPStatus.OK, {}