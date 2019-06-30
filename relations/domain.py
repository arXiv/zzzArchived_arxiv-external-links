"""Core domain concepts and rules."""

from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple, Optional, Any

ArXivID = str
RelationID = str


def resolve_arxiv_id(s: str) -> ArXivID:
    """Resolve string that represents an arXiv ID to ArXivID."""
    return s


def resolve_relation_id(s: str) -> RelationID:
    """Resolve string that represents a relation ID to RelationID."""
    return s


class EPrint(NamedTuple):
    """Info of E-print."""

    arxiv_id: ArXivID
    version: int


class RelationType(Enum):
    """Type of relations."""

    ADD = auto()
    EDIT = auto()
    SUPPRESS = auto()


class Resource(NamedTuple):
    """Domain class of resources."""

    resource_type: str
    identifier: str


class Relation(NamedTuple):
    """The core domain class of relations."""

    identifier: RelationID
    relation_type: RelationType
    e_print: EPrint
    resource: Resource
    description: str
    added_at: datetime
    creator: Optional[str]
    supercedes_or_suppresses: Optional[RelationID]


def support_json_default(o: Any) -> Any:
    """Support JSON serialization of Relation."""
    if isinstance(o, RelationType):
        if o == RelationType.ADD:
            return "ADD"
        elif o == RelationType.EDIT:
            return "EDIT"
        else:  # RelationType.SUPPRESS
            return "SUPPRESS"
    elif isinstance(o, datetime):
        return o.isoformat()

    raise TypeError(repr(o) + " is not JSON serializable")
