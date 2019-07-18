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

        self.prev_data = dict(arxiv_id=resolve_arxiv_id("1234.78901"),  # type: ignore
                              arxiv_ver=2,
                              supercedes_or_suppresses=None,
                              rel_type=RelationType.ADD,
                              resource_type="DOI",
                              resource_id="10.1023/hage.2018.7.11",
                              description="test",
                              creator="tester",
                              added_at=datetime.now())
        self.relDB = self.create.RelationDB(**self.prev_data)  # type: ignore
        self.create.db.session.add(self.relDB)    # type: ignore
        self.create.db.session.commit()     # type: ignore

    def tearDown(self) -> None:
        """Clear the database and tear down all tables."""
        self.create.db.session.remove()  # type: ignore
        self.create.db.drop_all()    # type: ignore

    def test_create(self) -> None:
        """Add new relation."""
        rel = self.create.create(resolve_arxiv_id("1234.56789"),  # type: ignore
                                 1,
                                 "DOI",
                                 "10.1023/hoge.2013.7.24",
                                 "test",
                                 "tester")

        session = self.create.db.session   # type: ignore
        query = session.query(self.create.RelationDB)  # type: ignore
        rel_db = query.get(rel.identifier)  # type: ignore

        # check the created relation is valid
        self.assertEqual(rel.relation_type, RelationType.ADD)
        self.assertEqual(rel.e_print.arxiv_id, "1234.56789")
        self.assertEqual(rel.e_print.version, 1)
        self.assertEqual(rel.resource.resource_type, "DOI")
        self.assertEqual(rel.resource.identifier, "10.1023/hoge.2013.7.24")
        self.assertEqual(rel.description, "test")
        self.assertEqual(rel.creator, "tester")
        self.assertEqual(rel.supercedes_or_suppresses, None)

        # check the record is cetainly created on DB
        self.assertEqual(rel_db.rel_type, RelationType.ADD)
        self.assertEqual(rel_db.arxiv_id, "1234.56789")
        self.assertEqual(rel_db.arxiv_ver, 1)
        self.assertEqual(rel_db.resource_type, "DOI")
        self.assertEqual(rel_db.resource_id, "10.1023/hoge.2013.7.24")
        self.assertEqual(rel_db.description, "test")
        self.assertEqual(rel_db.added_at, rel.added_at)
        self.assertEqual(rel_db.creator, "tester")
        self.assertEqual(rel_db.supercedes_or_suppresses, None)

    def test_supercede(self) -> None:
        """Add new relation that supercedes another."""
        rel = self.create.supercede(resolve_arxiv_id("1234.78901"),  # type: ignore
                                    2,
                                    str(self.relDB.id),
                                    "DOI",
                                    "10.1023/hage.2018.7.13",
                                    "test",
                                    "tester")

        session = self.create.db.session   # type: ignore
        query = session.query(self.create.RelationDB)  # type: ignore
        rel_db = query.get(rel.identifier)  # type: ignore

        # check the created relation is valid
        self.assertEqual(rel.relation_type, RelationType.EDIT)
        self.assertEqual(rel.e_print.arxiv_id, "1234.78901")
        self.assertEqual(rel.e_print.version, 2)
        self.assertEqual(rel.resource.resource_type, "DOI")
        self.assertEqual(rel.resource.identifier, "10.1023/hage.2018.7.13")
        self.assertEqual(rel.description, "test")
        self.assertEqual(rel.creator, "tester")
        self.assertEqual(rel.supercedes_or_suppresses, self.relDB.id)

        # check the record is cetainly created on DB
        self.assertEqual(rel_db.rel_type, RelationType.EDIT)
        self.assertEqual(rel_db.arxiv_id, "1234.78901")
        self.assertEqual(rel_db.arxiv_ver, 2)
        self.assertEqual(rel_db.resource_type, "DOI")
        self.assertEqual(rel_db.resource_id, "10.1023/hage.2018.7.13")
        self.assertEqual(rel_db.description, "test")
        self.assertEqual(rel_db.added_at, rel.added_at)
        self.assertEqual(rel_db.creator, "tester")
        self.assertEqual(rel_db.supercedes_or_suppresses, self.relDB.id)

    def test_suppress(self) -> None:
        """Add new relation that suppresses another."""
        rel = self.create.suppress(resolve_arxiv_id("1234.78901"),  # type: ignore
                                   2,
                                   str(self.relDB.id),
                                   "test",
                                   "tester")

        session = self.create.db.session   # type: ignore
        query = session.query(self.create.RelationDB)  # type: ignore
        rel_db = query.get(rel.identifier)  # type: ignore

        # check the created relation is valid
        self.assertEqual(rel.relation_type, RelationType.SUPPRESS)
        self.assertEqual(rel.e_print.arxiv_id, "1234.78901")
        self.assertEqual(rel.e_print.version, 2)
        self.assertEqual(rel.resource.resource_type, "DOI")
        self.assertEqual(rel.resource.identifier, "10.1023/hage.2018.7.11")
        self.assertEqual(rel.description, "test")
        self.assertEqual(rel.creator, "tester")
        self.assertEqual(rel.supercedes_or_suppresses, self.relDB.id)

        # check the record is cetainly created on DB
        self.assertEqual(rel_db.rel_type, RelationType.SUPPRESS)
        self.assertEqual(rel_db.arxiv_id, "1234.78901")
        self.assertEqual(rel_db.arxiv_ver, 2)
        self.assertEqual(rel_db.resource_type, "DOI")
        self.assertEqual(rel_db.resource_id, "10.1023/hage.2018.7.11")
        self.assertEqual(rel_db.description, "test")
        self.assertEqual(rel_db.added_at, rel.added_at)
        self.assertEqual(rel_db.creator, "tester")
        self.assertEqual(rel_db.supercedes_or_suppresses, self.relDB.id)


class TestRelationGetter(TestCase):
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

        # add relation data
        self.data = [dict(arxiv_id=resolve_arxiv_id("1234.56789"),  # type: ignore
                          arxiv_ver=1,
                          supercedes_or_suppresses=None,
                          rel_type=RelationType.ADD,
                          resource_type="DOI",
                          resource_id="10.1023/hoge.2013.7.24",
                          description="test",
                          creator="tester",
                          added_at=datetime.now()),
                     dict(arxiv_id=resolve_arxiv_id("1234.78901"),  # type: ignore
                          arxiv_ver=2,
                          supercedes_or_suppresses=None,
                          rel_type=RelationType.ADD,
                          resource_type="DOI",
                          resource_id="10.1023/hage.2018.7.11",
                          description="test",
                          creator="tester",
                          added_at=datetime.now()),
                     dict(arxiv_id=resolve_arxiv_id("1234.78901"),  # type: ignore
                          arxiv_ver=2,
                          supercedes_or_suppresses=2,
                          rel_type=RelationType.EDIT,
                          resource_type="DOI",
                          resource_id="10.1023/hage.2018.7.13",
                          description="test",
                          creator="tester",
                          added_at=datetime.now())]
        self.relDBs = [self.get.RelationDB(**d) for d in self.data]  # type: ignore
        for d in self.relDBs:
            self.get.db.session.add(d)    # type: ignore
        self.get.db.session.commit()     # type: ignore

    def tearDown(self) -> None:
        """Clear the database and tear down all tables."""
        self.get.db.session.remove()  # type: ignore
        self.get.db.drop_all()  # type: ignore

    def test_get_a_relation_that_exists(self) -> None:
        """When the relation exists, returns a :class:`.Relation`."""
        rel = self.get.from_id(1)  # type: ignore
        self.assertIsInstance(rel, Relation)
        self.assertEqual(rel.identifier, '1')
        self.assertEqual(rel.e_print.arxiv_id, self.data[0]['arxiv_id'])
        self.assertEqual(rel.e_print.version, self.data[0]['arxiv_ver'])
        self.assertEqual(rel.relation_type, self.data[0]['rel_type'])
        self.assertEqual(rel.resource.resource_type,
                         self.data[0]['resource_type'])
        self.assertEqual(rel.resource.identifier,
                         self.data[0]['resource_id'])
        self.assertEqual(rel.description, self.data[0]['description'])
        self.assertEqual(rel.creator, self.data[0]['creator'])
        self.assertEqual(rel.added_at, self.data[0]['added_at'])
        self.assertEqual(rel.supercedes_or_suppresses,
                         self.data[0]['supercedes_or_suppresses'])

    def test_get_a_relation_that_doesnt_exist(self) -> None:
        """When the relation doesn't exist, raises NotFoundError."""
        with self.assertRaises(self.get.NotFoundError):  # type: ignore
            self.get.from_id(5)  # type: ignore

    @mock.patch('relations.services.get.db.session.query')
    def test_get_a_relation_when_db_is_unavailable(self,
                                                   mock_query: Any) -> None:
        """When the database squawks, raises an IOError."""
        def raise_op_error(*args: str, **kwargs: str) -> None:
            raise sqlalchemy.exc.OperationalError('statement', {}, None)
        mock_query.side_effect = raise_op_error
        with self.assertRaises(self.get.DBLookUpError):  # type: ignore
            self.get.from_id(1)  # type: ignore

    def test_get_all_relations_from_e_print(self) -> None:
        """Return all :class:`.Relation`s."""
        rels = self.get.from_e_print("1234.78901", 2, active_only=False)  # type: ignore
        self.assertEqual(len(rels), 2)

    def test_get_active_relations_from_e_print(self) -> None:
        """Return all :class:`.Relation`s."""
        rels = self.get.from_e_print("1234.78901", 2, active_only=True)  # type: ignore
        self.assertEqual(len(rels), 1)
