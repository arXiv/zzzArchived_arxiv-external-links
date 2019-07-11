"""Service for relation retrlieval."""
from relations.domain import EPrint, Resource, Relation, RelationID, \
    RelationType
from .model import db, RelationDB


class NotFoundError(Exception):
    """Error that the retrieved relation cannot be found."""

    pass


class DBLookUpError(Exception):
    """Error that happens in lookup."""

    pass


def from_id(id: RelationID) -> Relation:
    """Retrieve a relation from an ID."""
    # query to DB
    try:
        rels = db.session.query(RelationDB) \
            .filter(RelationDB.id == int(id)) \
            .limit(1) \
            .all()
    except Exception as e:
        raise DBLookUpError from e

    # there must be only one entry
    if len(rels) == 0:
        raise NotFoundError
    rel_data = rels[0]

    # return the result
    return Relation(
        identifier=rel_data.id,
        relation_type=RelationType(rel_data.rel_type),
        e_print=EPrint(
            arxiv_id=rel_data.arxiv_id,
            version=rel_data.arxiv_ver
        ),
        resource=Resource(
            resource_type=rel_data.resource_type,
            identifier=rel_data.resource_id
        ),
        description=rel_data.description,
        added_at=rel_data.added_at,
        creator=rel_data.creator,
        supercedes_or_suppresses=rel_data.supercedes_or_suppresses
    )
