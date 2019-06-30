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
from domain import Relation, RelationID, RelationType, ArXivID, \
    resolve_arxiv_id, resolve_relation_id
from services.create import create
from services.get import from_id, NotFoundError

Response = Tuple[Dict[str, Any], HTTPStatus, Dict[str, str]]


def service_status(params: MultiDict) -> Response:
    """
    Handle requests for the service status endpoint.

    Returns ``200 OK`` if the service is up and ready to handle requests.
    """
    return {'iam': 'ok'}, HTTPStatus.OK, {}


def create_new(arxiv_id_str: str,
               arxiv_ver: int,
               resource_type: str,
               resource_id: str,
               description: str,
               creator: str) -> Response:
    """
    Create a new relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.

    arxiv_ver: int
        The version of the e-print.

    resource_type: str
        The type of the corresponding resource.

    resource_id: str
        An identifier of the resource e.g., DOI.

    description: str
        A description for the relation.

    creator: str
        Info of the user/app who requested this relation creation.

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
    rel: Relation = create(arxiv_id,
                           arxiv_ver,
                           None,
                           RelationType.ADD,
                           resource_type,
                           resource_id,
                           description,
                           creator)

    # create the result value
    result: Dict[str, Any] = {str(rel.identifier): json.dumps(rel)}

    # return
    return result, HTTPStatus.OK, {}


def supercede(arxiv_id_str: str,
              arxiv_ver: int,
              relation_id_str: str,
              resource_type: str,
              resource_id: str,
              description: str,
              creator: str) -> Response:
    """
    Create a new relation that supercedes an existing relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.

    arxiv_ver: int
        The version of the e-print.

    relation_id_str: str
        THe relation ID to be superceded.

    resource_type: str
        The type of the corresponding resource.

    resource_id: str
        An identifier of the resource e.g., DOI.

    description: str
        A description for the relation.

    creator: str
        Info of the user/app who requested this relation creation.

    Returns
    -------
    dict: Dict[str, Any]
        A relation ID as a key and the corresponding relation as its value.
        Blank if it fails.

    HTTPStatus
        An HTTP status code.

    dict: Dict[str, str]
        The previous relation ID if it succeeds, or an error message otherwise.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    prev_rel_id: RelationID = resolve_relation_id(relation_id_str)
    try:
        # try get the previous relation
        from_id(prev_rel_id)

    except NotFoundError:
        return {}, \
                HTTPStatus.INTERNAL_SERVER_ERROR, \
                {"error": "The previous relation cannot be found"}

    # get new relations that supercedes the prev
    new_rel: Relation = create(arxiv_id,
                               arxiv_ver,
                               prev_rel_id,
                               RelationType.EDIT,
                               resource_type,
                               resource_id,
                               description,
                               creator)

    # create the result value
    result: Dict[str, Any] = {str(new_rel.identifier): json.dumps(new_rel)}

    # return
    return result, HTTPStatus.OK, {"previous": relation_id_str}


def suppress(arxiv_id_str: str,
             arxiv_ver: int,
             relation_id_str: str,
             description: str,
             creator: str) -> Response:
    """
    Create a new relation that suppresses an existing relation for an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.

    arxiv_ver: int
        The version of the e-print.

    relation_id_str: str
        THe relation ID to be superceded.

    description: str
        A description for the relation.

    creator: str
        Info of the user/app who requested this relation creation.

    Returns
    -------
    dict: Dict[str, Any]
        A relation ID as a key and the corresponding relation as its value.
        Blank if it fails.

    HTTPStatus
        An HTTP status code.

    dict: Dict[str, str]
        The previous relation ID if it succeeds, or an error message otherwise.

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
                                   description,
                                   creator)

        # create the result value
        result: Dict[str, Any] = {str(new_rel.identifier): json.dumps(new_rel)}

        # return
        return result, HTTPStatus.OK, {"previous": relation_id_str}

    except NotFoundError:
        return {}, \
                HTTPStatus.INTERNAL_SERVER_ERROR, \
                {"error": "The previous relation cannot be found"}
