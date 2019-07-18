"""Service for relation retrlieval."""
from typing import List
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound
from relations.domain import EPrint, Resource, Relation, RelationID, \
    ArXivID, RelationType
from .model import db, RelationDB
from .util import relation_from_DB


class NotFoundError(Exception):
    """Error that the retrieved relation cannot be found."""


class DBLookUpError(Exception):
    """Error that happens in lookup."""


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


def is_active(relation_id: RelationID) -> bool:
    """Retrieve an activation record from a relation ID."""
    # query to DB
    try:
        sups = db.session.query(RelationDB) \
            .filter(RelationDB.supercedes_or_suppresses == int(relation_id)) \
            .first()
    except Exception as e:
        raise DBLookUpError from e

    # return true if there is no superceder/suppressor
    return bool(sups is None)


def from_e_print(arxiv_id: ArXivID,
                 arxiv_ver: int,
                 active_only: bool = True) -> List[Relation]:
    """Retrieve relations associated with an e-print."""
    # query to DB
    try:
        if active_only:
            sups = db.session.query(RelationDB.supercedes_or_suppresses) \
                .filter(RelationDB.arxiv_id == str(arxiv_id),
                        RelationDB.arxiv_ver == arxiv_ver,
                        ~RelationDB.supercedes_or_suppresses.is_(None))
            rels = db.session.query(RelationDB) \
                .filter(RelationDB.arxiv_id == str(arxiv_id),
                        RelationDB.arxiv_ver == arxiv_ver,
                        ~RelationDB.id.in_(sups)) \
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
        new_rel = relation_from_DB(rel_data)
        result.append(new_rel)
    return result
