"""Service for new relation creation."""

from datetime import datetime
from typing import Optional
from relations.domain import ArXivID, EPrint, Relation, RelationID, \
    RelationType, Resource
from .model import db, RelationDB


class StorageError(Exception):
    """Error that happens in strage of data."""


def create(arxiv_id: ArXivID,
           arxiv_ver: int,
           relation_id: Optional[RelationID],
           relation_type: RelationType,
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
    relation_type: RelationType
        THe type of this relation i.e., ADD, EDIT, or SUPPRESS.
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
    rel_data = RelationDB(rel_type=relation_type,
                          arxiv_id=str(arxiv_id),
                          arxiv_ver=arxiv_ver,
                          resource_type=resource_type,
                          resource_id=resource_id,
                          description=description,
                          added_at=datetime.now(),
                          creator=creator,
                          supercedes_or_suppresses=relation_id)
    try:
        db.session.add(rel_data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise StorageError from e

    # return the result
    return Relation(
        identifier=rel_data.id,
        relation_type=relation_type,
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
