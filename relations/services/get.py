"""Service for relation retrlieval."""
from typing import List
from sqlalchemy.orm.exc import NoResultFound
from relations.domain import EPrint, Resource, Relation, RelationID, \
    ArXivID, RelationType
from .model import db, RelationDB, ActivationDB
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
        rel_data = db.session.query(ActivationDB) \
            .filter(ActivationDB.id == int(relation_id)) \
            .one()
    except NoResultFound as nrf:
        raise NotFoundError from nrf
    except Exception as e:
        raise DBLookUpError from e

    # return the result
    return bool(rel_data.active)


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
