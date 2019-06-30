"""Service for relation retrlieval."""
from domain import Relation, RelationID


class NotFoundError(Exception):
    """Error that the retrieved relation cannot be found."""

    pass  # not implemented yet


def from_id(id: RelationID) -> Relation:
    """Retrieve a relation from an ID."""
    pass  # not implemented yet
