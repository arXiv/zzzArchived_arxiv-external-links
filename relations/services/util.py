"""Util functions."""
from relations.domain import Relation, RelationType, EPrint, Resource
from .model import RelationDB


def relation_from_DB(rel_data: RelationDB) -> Relation:
    """Retrieve a relation from a result of DB query."""
    return Relation(
        identifier=str(rel_data.id),
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
