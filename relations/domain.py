"""Core domain concepts and rules."""

from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple, Optional

ArXivID = str
ResourceType = str
RelationID = str


class EPrint(NamedTuple):
    """Info of E-print."""

    arxiv_id: ArXivID
    version: int


class RelationType(Enum):
    """Type of relations."""

    ADD = auto()
    EDIT = auto()
    DEACTIVATE = auto()


class Relation(NamedTuple):
    """The core domain class of relations."""

    identifier: RelationID
    relation_type: RelationType
    e_print: EPrint
    resource_type: ResourceType
    resource_id: str
    description: str
    added_at: datetime
    creator: Optional[str]
    superceded_or_suppressed: Optional[RelationID]
