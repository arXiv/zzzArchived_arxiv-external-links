"""Service for relation retrlieval."""
from typing import List
from sqlalchemy.orm.exc import NoResultFound
from relations.domain import EPrint, Resource, Relation, RelationID, \
    ArXivID, RelationType
from .model import db, RelationDB, ActivationDB


class NotFoundError(Exception):
    """Error that the retrieved relation cannot be found."""


class DBLookUpError(Exception):
    """Error that happens in lookup."""


def relation_from_DB(rel_data: RelationDB) -> Relation:
    """Retrieve a relation from a result of DB query."""
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


def from_id(id: RelationID) -> Relation:
    """Retrieve a relation from an ID."""
    # query to DB
    try:
        rel_data = db.session.query(RelationDB) \
            .filter(RelationDB.id == int(id)) \
            .one()
    except NoResultFound as nrf:
        raise NotFoundError from nrf
    except Exception as e:
        raise DBLookUpError from e

    # return the result
    return relation_from_DB(rel_data)


def from_e_print(arxiv_id: ArXivID,
                 arxiv_ver: int,
                 active_only: bool = True) -> List[Relation]:
    """Retrieve relations associated with an e-print."""
    # query to DB
    try:
        if active_only:
            rels = db.session.query(RelationDB, ActivationDB) \
                .join(RelationDB, RelationDB.id == ActivationDB.id) \
                .filter(RelationDB.arxiv_id == str(arxiv_id),
                        RelationDB.arxiv_ver == arxiv_ver,
                        ActivationDB.active) \
                .all()
        else:
            rels = db.session.query(RelationDB) \
                .filter(RelationDB.arxiv_id == str(arxiv_id),
                        RelationDB.arxiv_ver == arxiv_ver) \
                .all()
    except Exception as e:
        raise DBLookUpError from e

    # return the result
    result: List[Relation] = []
    for rel_data in rels:
        # if active only, rel_data is a tuple so extract the element
        rel_data = rel_data[0] if active_only else rel_data
        new_rel = relation_from_DB(rel_data)
        result.append(new_rel)
    return result
