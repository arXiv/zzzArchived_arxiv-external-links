"""
Request controllers for the external links service.

These may be used handle requests originating from the :mod:`.routes.api`
and/or the :mod:`.routes.ui`.

If the behavior of these controllers diverges along the UI/API lines, then we
can split this into ``controllers/api.py`` and ``controllers/ui.py``.
"""

from typing import Tuple, Any, Dict, List
from http import HTTPStatus
import json

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import InternalServerError
from relations.domain import Relation, RelationID, RelationType, ArXivID, \
    resolve_arxiv_id, resolve_relation_id, support_json_default
from relations.services.create import create, StorageError
from relations.services.get import from_id, NotFoundError

Response = Tuple[Dict[str, Any], HTTPStatus, Dict[str, str]]


def service_status(params: MultiDict) -> Response:
    """
    Handle requests for the service status endpoint.

    Returns ``200 OK`` if the service is up and ready to handle requests.
    """
    return {'iam': 'ok'}, HTTPStatus.OK, {}


def create_new(arxiv_id_str: str,
               arxiv_ver: int,
               payload: Dict[str, Any]) -> Response:
    """
    Create a new relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    payload: Dict[str, Any]
        Payload info.

    Returns
    -------
    Dict[str, Any]
        The newly-created relations, whose key is an ID,
            and whose value is the corresponding relation in JSON format.
        Blank if it fails.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        A blank dict.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    # get relation
    try:
        rel: Relation = create(arxiv_id,
                               arxiv_ver,
                               None,
                               RelationType.ADD,
                               payload['resource_type'],
                               payload['resource_id'],
                               payload.get('description', ''),
                               payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = \
            {str(rel.identifier): json.dumps(rel, default=support_json_default)}

        # return
        return result, HTTPStatus.OK, {}

    except KeyError as ke:
        raise InternalServerError(f"A value of {str(ke)} not found")

    except StorageError as se:
        raise InternalServerError("An error occured in storage") from se


def supercede(arxiv_id_str: str,
              arxiv_ver: int,
              relation_id_str: str,
              payload: Dict[str, Any]) -> Response:
    """
    Create a new relation that supercedes an existing relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    relation_id_str: str
        The previous relation ID to be superceded.
    payload: Dict[str, Any]
        Payload info.

    Returns
    -------
    Dict[str, Any]
        A relation ID as a key and the corresponding relation as its value.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        The previous relation ID.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    prev_rel_id: RelationID = resolve_relation_id(relation_id_str)
    try:
        # try get the previous relation
        from_id(prev_rel_id)

        # get new relations that supercedes the prev
        new_rel: Relation = create(arxiv_id,
                                   arxiv_ver,
                                   prev_rel_id,
                                   RelationType.EDIT,
                                   payload['resource_type'],
                                   payload['resource_id'],
                                   payload.get('description', ''),
                                   payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = \
            {str(new_rel.identifier):
             json.dumps(new_rel, default=support_json_default)}

        # return
        return result, HTTPStatus.OK, {"previous": relation_id_str}

    except KeyError as ke:
        raise InternalServerError(f"A value of {str(ke)} not found")

    except NotFoundError as nfe:
        raise InternalServerError("The previous relation cannot be found") \
            from nfe

    except StorageError as se:
        raise InternalServerError("An error occured in storage") from se


def suppress(arxiv_id_str: str,
             arxiv_ver: int,
             relation_id_str: str,
             payload: Dict[str, Any]) -> Response:
    """
    Create a new relation that suppresses an existing relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    relation_id_str: str
        The previous relation ID to be suppressed.
    payload: Dict[str, Any]
        Payload info.

    Returns
    -------
    Dict[str, Any]
        A relation ID as a key and the corresponding relation as its value.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        The previous relation ID.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    prev_rel_id: RelationID = resolve_relation_id(relation_id_str)
    try:
        # get the previous relation
        prev_rel: Relation = from_id(prev_rel_id)

        # get new relations that supercedes the prev
        new_rel: Relation = create(arxiv_id,
                                   arxiv_ver,
                                   prev_rel_id,
                                   RelationType.SUPPRESS,
                                   prev_rel.resource.resource_type,
                                   prev_rel.resource.identifier,
                                   payload.get('escription', ''),
                                   payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = \
            {str(new_rel.identifier):
             json.dumps(new_rel, default=support_json_default)}

        # return
        return result, HTTPStatus.OK, {"previous": relation_id_str}

    except NotFoundError as nfe:
        raise InternalServerError("The previous relation cannot be found") \
            from nfe

    except StorageError as se:
        raise InternalServerError("An error occured in storage") from se
