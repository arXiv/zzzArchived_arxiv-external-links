"""
Request controllers for the external links service.

These may be used handle requests originating from the :mod:`.routes.api`
and/or the :mod:`.routes.ui`.

If the behavior of these controllers diverges along the UI/API lines, then we
can split this into ``controllers/api.py`` and ``controllers/ui.py``.
"""

from typing import Tuple, Any, Dict, List
from http import HTTPStatus
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import InternalServerError
from relations.domain import Relation, RelationID, RelationType, ArXivID, \
    resolve_arxiv_id, resolve_relation_id
from relations.services import create
from relations.services.create import StorageError
from relations.services.get import from_id, is_active, from_e_print, \
    NotFoundError, DBLookUpError

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
        The newly-created relation.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        A blank dict.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    # get relation
    try:
        rel: Relation = create.create(arxiv_id,
                                      arxiv_ver,
                                      payload['resource_type'],
                                      payload['resource_id'],
                                      payload.get('description', ''),
                                      payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = rel._asdict()

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
        The newly-created relation.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        A blank dict.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    prev_rel_id: RelationID = resolve_relation_id(relation_id_str)
    try:
        # check if the previous relation is active
        if not is_active(prev_rel_id):
            raise InternalServerError("The previous relation is already inactive.")

        # get new relations that supercedes the prev
        new_rel: Relation = create.supercede(arxiv_id,
                                             arxiv_ver,
                                             prev_rel_id,
                                             payload['resource_type'],
                                             payload['resource_id'],
                                             payload.get('description', ''),
                                             payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = new_rel._asdict()

        # return
        return result, HTTPStatus.OK, {}

    except KeyError as ke:
        raise InternalServerError(f"A value of {str(ke)} not found")

    except NotFoundError as nfe:
        raise InternalServerError("The previous relation cannot be found") \
            from nfe

    except DBLookUpError as lue:
        raise InternalServerError("A failure occured in "
                                  "looking up the previous relation") \
            from lue

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
        The newly-created relation.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        A blank dict.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)

    prev_rel_id: RelationID = resolve_relation_id(relation_id_str)
    try:
        # try get the previous relation -- needs to exist
        from_id(prev_rel_id)

        # check if the previous relation is active
        if not is_active(prev_rel_id):
            raise InternalServerError("The previous relation is already inactive.")

        # get new relations that supercedes the prev
        new_rel: Relation = create.suppress(arxiv_id,
                                            arxiv_ver,
                                            prev_rel_id,
                                            payload.get('description', ''),
                                            payload.get('creator'))

        # create the result value
        result: Dict[str, Any] = new_rel._asdict()

        # return
        return result, HTTPStatus.OK, {}

    except NotFoundError as nfe:
        raise InternalServerError("The previous relation cannot be found") \
            from nfe

    except DBLookUpError as lue:
        raise InternalServerError("A failure occured in "
                                  "looking up the previous relation") \
            from lue

    except StorageError as se:
        raise InternalServerError("An error occured in storage") from se


def retrieve(arxiv_id_str: str,
             arxiv_ver: int,
             active_only: bool) -> Response:
    """
    Retrieve relations associated with an e-print.

    Parameters
    ----------
    arxiv_id_str: str
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    active_only: bool
        When it is true, the return value will only include active links.

    Returns
    -------
    Dict[str, Any]
        A collection of relations. it contains e-print ID and version, and
        a list of corresponding relations.
    HTTPStatus
        An HTTP status code.
    Dict[str, str]
        blank.

    """
    # get arxiv ID from str
    arxiv_id: ArXivID = resolve_arxiv_id(arxiv_id_str)
    try:
        # retrieve
        rels: List[Relation] = from_e_print(arxiv_id, arxiv_ver, active_only)
        dicts: List[Dict[str, Any]] = list(map(lambda x: x._asdict(), rels))

    except DBLookUpError as lue:
        raise InternalServerError("A failure occured in looking up relations") \
            from lue

    # encode to response
    result: Dict[str, Any] = {"arxiv_id": arxiv_id,
                              "version": arxiv_ver,
                              "relations": dicts}
    return result, HTTPStatus.OK, {}
