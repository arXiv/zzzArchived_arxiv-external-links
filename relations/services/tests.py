"""Tests for relations services."""

from datetime import datetime
from unittest import TestCase, mock
import sqlalchemy
from typing import Any
from relations.domain import Relation, RelationType, resolve_arxiv_id


class TestRelationCreator(TestCase):
    """:func:`.create.create` creates a new record in the database."""

    def setUp(self) -> None:
        """Initialize an in-memory SQLite database."""
        from relations.services import create
        self.create = create
        app = mock.MagicMock(
            config={
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False
            }, extensions={}, root_path=''
        )
        self.create.db.init_app(app)    # type: ignore
        self.create.db.app = app    # type: ignore
        self.create.db.create_all()  # type: ignore

    def tearDown(self) -> None:
        """Clear the database and tear down all tables."""
        self.create.db.session.remove()  # type: ignore
        self.create.db.drop_all()    # type: ignore

    def test_create(self) -> None:
        """Add new relation."""
        rel = self.create.create(resolve_arxiv_id("1234.56789"),  # type: ignore
                                 1,
                                 None,
                                 RelationType.ADD,
                                 "DOI",
                                 "10.1023/hoge.2013.7.24",
                                 "test",
                                 "tester")
        self.assertGreater(rel.identifier,
                           0,
                           "Relation.identifier is updated with pk id")

        session = self.create.db.session   # type: ignore
        query = session.query(self.create.RelationDB)  # type: ignore
        rel_db = query.get(rel.identifier)  # type: ignore

        self.assertEqual(rel_db.rel_type, rel.relation_type)
        self.assertEqual(rel_db.arxiv_id, rel.e_print.arxiv_id)
        self.assertEqual(rel_db.arxiv_ver, rel.e_print.version)
        self.assertEqual(rel_db.resource_type, rel.resource.resource_type)
        self.assertEqual(rel_db.resource_id, rel.resource.identifier)
        self.assertEqual(rel_db.description, rel.description)
        self.assertEqual(rel_db.added_at, rel.added_at)
        self.assertEqual(rel_db.creator, rel.creator)
        self.assertEqual(rel_db.supercedes_or_suppresses,
                         rel.supercedes_or_suppresses)


class TestThingGetter(TestCase):
    """:mod:`.get` retrieves relations."""

    def setUp(self) -> None:
        """Initialize an in-memory SQLite database."""
        from relations.services import get
        self.get = get
        app = mock.MagicMock(
            config={
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False
            }, extensions={}, root_path=''
        )
        get.db.init_app(app)
        get.db.app = app
        get.db.create_all()

        self.data = dict(arxiv_id=resolve_arxiv_id("1234.56789"),  # type: ignore
                         arxiv_ver=1,
                         supercedes_or_suppresses=None,
                         rel_type=RelationType.ADD,
                         resource_type="DOI",
                         resource_id="10.1023/hoge.2013.7.24",
                         description="test",
                         creator="tester",
                         added_at=datetime.now())
        self.relDB = self.get.RelationDB(**self.data)     # type: ignore
        self.get.db.session.add(self.relDB)    # type: ignore
        self.get.db.session.commit()     # type: ignore

    def tearDown(self) -> None:
        """Clear the database and tear down all tables."""
        self.get.db.session.remove()  # type: ignore
        self.get.db.drop_all()  # type: ignore

    def test_get_a_relation_that_exists(self) -> None:
        """When the relation exists, returns a :class:`.Relation`."""
        rel = self.get.from_id(1)  # type: ignore
        self.assertIsInstance(rel, Relation)
        self.assertEqual(rel.identifier, 1)
        self.assertEqual(rel.e_print.arxiv_id, self.data['arxiv_id'])
        self.assertEqual(rel.e_print.version, self.data['arxiv_ver'])
        self.assertEqual(rel.relation_type, self.data['rel_type'])
        self.assertEqual(rel.resource.resource_type,
                         self.data['resource_type'])
        self.assertEqual(rel.resource.identifier,
                         self.data['resource_id'])
        self.assertEqual(rel.description, self.data['description'])
        self.assertEqual(rel.creator, self.data['creator'])
        self.assertEqual(rel.added_at, self.data['added_at'])
        self.assertEqual(rel.supercedes_or_suppresses,
                         self.data['supercedes_or_suppresses'])

    def test_get_a_relation_that_doesnt_exist(self) -> None:
        """When the thing doesn't exist, returns None."""
        with self.assertRaises(self.get.NotFoundError):  # type: ignore
            self.get.from_id(2)  # type: ignore

    @mock.patch('relations.services.get.db.session.query')
    def test_get_a_relation_when_db_is_unavailable(self,
                                                   mock_query: Any) -> None:
        """When the database squawks, raises an IOError."""
        def raise_op_error(*args: str, **kwargs: str) -> None:
            raise sqlalchemy.exc.OperationalError('statement', {}, None)
        mock_query.side_effect = raise_op_error
        with self.assertRaises(self.get.DBLookUpError):  # type: ignore
            self.get.from_id(1)  # type: ignore
