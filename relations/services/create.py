"""Service for new relation creation."""

from datetime import datetime
from typing import Optional
from pytz import UTC
from relations.domain import ArXivID, EPrint, Relation, RelationID, \
    RelationType, Resource
from .get import from_id
from .model import db, RelationDB
from .util import relation_from_DB


class StorageError(Exception):
    """Error that happens in strage of data."""


def create(arxiv_id: ArXivID,
           arxiv_ver: int,
           resource_type: str,
           resource_id: str,
           description: str,
           creator: Optional[str]) -> Relation:
    """
    Create a new relation for an e-print.

    Parameters
    ----------
    arxiv_id: ArXivID
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    resource_type: str
        The type of the corresponding resource.
    resource_id: str
        An identifier of the resource e.g., DOI.
    description: str
        A description for the relation.
    creator: Optional[str]
        Info of the user/app who requested this relation creation.

    Returns
    -------
    Relation
        The newly-created relation.

    """
    # store it to DB
    rel_data = RelationDB(rel_type=RelationType.ADD,
                          arxiv_id=str(arxiv_id),
                          arxiv_ver=arxiv_ver,
                          resource_type=resource_type,
                          resource_id=resource_id,
                          description=description,
                          added_at=datetime.now(UTC),
                          creator=creator,
                          supercedes_or_suppresses=None)
    try:
        db.session.add(rel_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return relation_from_DB(rel_data)


def supercede(arxiv_id: ArXivID,
              arxiv_ver: int,
              relation_id: RelationID,
              resource_type: str,
              resource_id: str,
              description: str,
              creator: Optional[str]) -> Relation:
    """
    Create a new relation for an e-print.

    Parameters
    ----------
    arxiv_id: ArXivID
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    relation_id: RelationID
        THe relation ID to be superceded.
    resource_type: str
        The type of the corresponding resource.
    resource_id: str
        An identifier of the resource e.g., DOI.
    description: str
        A description for the relation.
    creator: Optional[str]
        Info of the user/app who requested this relation creation.

    Returns
    -------
    Relation
        The newly-created relation.

    """
    # store it to DB
    rel_data = RelationDB(rel_type=RelationType.EDIT,
                          arxiv_id=str(arxiv_id),
                          arxiv_ver=arxiv_ver,
                          resource_type=resource_type,
                          resource_id=resource_id,
                          description=description,
                          added_at=datetime.now(UTC),
                          creator=creator,
                          supercedes_or_suppresses=relation_id)
    try:
        # check the previous relation
        prev_rel = from_id(relation_id)
        if prev_rel.relation_type == RelationType.SUPPRESS:
            raise StorageError('Cannot suppress a SUPPRESS relation')

        # register
        db.session.add(rel_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return relation_from_DB(rel_data)


def suppress(arxiv_id: ArXivID,
             arxiv_ver: int,
             relation_id: RelationID,
             description: str,
             creator: Optional[str]) -> Relation:
    """
    Create a new relation for an e-print.

    Parameters
    ----------
    arxiv_id: ArXivID
        The arXiv ID of the e-print.
    arxiv_ver: int
        The version of the e-print.
    relation_id: RelationID
        THe relation ID to be suppressed.
    description: str
        A description for the relation.
    creator: Optional[str]
        Info of the user/app who requested this relation creation.

    Returns
    -------
    Relation
        The newly-created relation.

    """
    try:
        # check the previous relation
        prev_rel = from_id(relation_id)
        if prev_rel.relation_type == RelationType.SUPPRESS:
            raise StorageError('Cannot suppress a SUPPRESS relation')

        # store it to DB
        rel_data = RelationDB(rel_type=RelationType.SUPPRESS,
                              arxiv_id=str(arxiv_id),
                              arxiv_ver=arxiv_ver,
                              resource_type=prev_rel.resource.resource_type,
                              resource_id=prev_rel.resource.identifier,
                              description=description,
                              added_at=datetime.now(UTC),
                              creator=creator,
                              supercedes_or_suppresses=str(relation_id))
        # register
        db.session.add(rel_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return relation_from_DB(rel_data)
