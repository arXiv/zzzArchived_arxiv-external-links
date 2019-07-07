"""Service for new relation creation."""

from datetime import datetime
from typing import Optional
from relations.domain import ArXivID, EPrint, Relation, RelationID, \
    RelationType, Resource
from .model import db, RelationDB, ActivationDB


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
                          added_at=datetime.now(),
                          creator=creator,
                          supercedes_or_suppresses=None)
    try:
        db.session.add(rel_data)
        activation = ActivationDB(id=rel_data.id,
                                  active=True)
        db.session.add(activation)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return Relation(
        identifier=rel_data.id,
        relation_type=RelationType.ADD,
        e_print=EPrint(
            arxiv_id=str(arxiv_id),
            version=arxiv_ver
        ),
        resource=Resource(
            resource_type=resource_type,
            identifier=resource_id
        ),
        description=description,
        added_at=rel_data.added_at,
        creator=creator,
        supercedes_or_suppresses=None
    )


def supercede(arxiv_id: ArXivID,
              arxiv_ver: int,
              relation_id: Optional[RelationID],
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
                          added_at=datetime.now(),
                          creator=creator,
                          supercedes_or_suppresses=str(relation_id))
    try:
        # deactivate the previous relation
        prev_act = db.session.query(ActivationDB) \
            .filter(ActivationDB.id == relation_id) \
            .one()
        prev_act.active = False

        # register
        db.session.add(rel_data)
        act_data = ActivationDB(id=rel_data.id,
                                active=True)
        db.session.add(act_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return Relation(
        identifier=rel_data.id,
        relation_type=RelationType.EDIT,
        e_print=EPrint(
            arxiv_id=str(arxiv_id),
            version=arxiv_ver
        ),
        resource=Resource(
            resource_type=resource_type,
            identifier=resource_id
        ),
        description=description,
        added_at=rel_data.added_at,
        creator=creator,
        supercedes_or_suppresses=rel_data.supercedes_or_suppresses
    )


def suppress(arxiv_id: ArXivID,
             arxiv_ver: int,
             relation_id: Optional[RelationID],
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
        # deactivate the previous relation
        prev_rel = db.session.query(RelationDB) \
            .filter(RelationDB.id == relation_id) \
            .one()

        # deactivate the previous relation
        prev_act = db.session.query(ActivationDB) \
            .filter(ActivationDB.id == relation_id) \
            .one()
        prev_act.active = False

        # store it to DB
        rel_data = RelationDB(rel_type=RelationType.SUPPRESS,
                              arxiv_id=str(arxiv_id),
                              arxiv_ver=arxiv_ver,
                              resource_type=prev_rel.resource_type,
                              resource_id=prev_rel.resource_id,
                              description=description,
                              added_at=datetime.now(),
                              creator=creator,
                              supercedes_or_suppresses=str(relation_id))
        # register
        db.session.add(rel_data)
        act_data = ActivationDB(id=rel_data.id,
                                active=True)
        db.session.add(act_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e


    # return the result
    return Relation(
        identifier=rel_data.id,
        relation_type=RelationType(rel_data.rel_type),
        e_print=EPrint(
            arxiv_id=str(arxiv_id),
            version=arxiv_ver
        ),
        resource=Resource(
            resource_type=rel_data.resource_type,
            identifier=rel_data.resource_id
        ),
        description=description,
        added_at=rel_data.added_at,
        creator=creator,
        supercedes_or_suppresses=str(relation_id)
    )
