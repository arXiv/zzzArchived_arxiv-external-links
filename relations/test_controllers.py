"""Tests for :mod: relations.controllers."""
import json
from http import HTTPStatus
from unittest import TestCase, mock
from datetime import datetime
from typing import Any
from relations.controllers import create_new, supercede, suppress
from relations.domain import Relation, RelationType, EPrint, Resource, \
    support_json_default
from relations.services.create import StorageError
from relations.services.get import NotFoundError


class TestRelationController(TestCase):
    """Test the :mod:`relations.controllers.hoge` controller."""

    @mock.patch('relations.controllers.create')
    def test_create_new_with_success(self, mock_create: Any) -> None:
        """:func:`.create_new` gets a relation."""
        rel = Relation(identifier="123",
                       relation_type=RelationType.ADD,
                       e_print=EPrint(arxiv_id="1234.56789",
                                      version=3),
                       resource=Resource(resource_type="DOI",
                                         identifier="10.1023/hoge.2013.7.24"),
                       description="test",
                       added_at=datetime(2019, 7, 1),
                       creator="tester",
                       supercedes_or_suppresses=None)
        mock_create.return_value = rel

        # test
        res1, status, res2 = create_new(rel.e_print.arxiv_id,
                                        rel.e_print.version,
                                        rel.resource.resource_type,
                                        rel.resource.identifier,
                                        rel.description,
                                        "tester")
        self.assertDictEqual(res1,
                             {rel.identifier: 
                              json.dumps(rel, default=support_json_default)})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertDictEqual(res2, {})

    @mock.patch('relations.controllers.create')
    def test_create_new_with_fail(self, mock_create: Any) -> None:
        """:func:`.create_new` fails in storage."""
        rel = Relation(identifier="123",
                       relation_type=RelationType.ADD,
                       e_print=EPrint(arxiv_id="1234.56789",
                                      version=3),
                       resource=Resource(resource_type="DOI",
                                         identifier="10.1023/hoge.2013.7.24"),
                       description="test",
                       added_at=datetime(2019, 7, 1),
                       creator="tester",
                       supercedes_or_suppresses=None)
        mock_create.side_effect = StorageError

        # test
        res1, status, res2 = create_new(rel.e_print.arxiv_id,
                                        rel.e_print.version,
                                        rel.resource.resource_type,
                                        rel.resource.identifier,
                                        rel.description,
                                        "tester")
        self.assertDictEqual(res1, {})
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertDictEqual(res2, {"error": "An error occured in storage"})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_supercede_with_success(self,
                                    mock_create: Any,
                                    mock_from_id: Any) -> None:
        """:func:`.supercede` gets a relation."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.return_value = prev_rel
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.EDIT,
                           e_print=EPrint(arxiv_id="1234.56789",
                                          version=3),
                           resource=Resource(resource_type="DOI",
                                             identifier="10.1023/hoge.2018.6.11"),
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.return_value = new_rel

        # test
        res1, status, res2 = supercede(new_rel.e_print.arxiv_id,
                                       new_rel.e_print.version,
                                       prev_rel.identifier,
                                       new_rel.resource.resource_type,
                                       new_rel.resource.identifier,
                                       new_rel.description,
                                       "new tester")
        self.assertDictEqual(res1,
                             {new_rel.identifier: 
                              json.dumps(new_rel, default=support_json_default)})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertDictEqual(res2, {"previous": prev_rel.identifier})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_supercede_with_fail1(self,
                                  mock_create: Any,
                                  mock_from_id: Any) -> None:
        """:func:`.supercede` fails in retrieving the old relation."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.side_effect = NotFoundError
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.EDIT,
                           e_print=EPrint(arxiv_id="1234.56789",
                                          version=3),
                           resource=Resource(resource_type="DOI",
                                             identifier="10.1023/hoge.2018.6.11"),
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.return_value = new_rel

        # test
        res1, status, res2 = supercede(new_rel.e_print.arxiv_id,
                                       new_rel.e_print.version,
                                       prev_rel.identifier,
                                       new_rel.resource.resource_type,
                                       new_rel.resource.identifier,
                                       new_rel.description,
                                       "new tester")
        self.assertDictEqual(res1, {})
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertDictEqual(res2, {"error": "The previous relation cannot be found"})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_supercede_with_fail2(self,
                                  mock_create: Any,
                                  mock_from_id: Any) -> None:
        """:func:`.supercede` gets a relation."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.return_value = prev_rel
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.EDIT,
                           e_print=EPrint(arxiv_id="1234.56789",
                                          version=3),
                           resource=Resource(resource_type="DOI",
                                             identifier="10.1023/hoge.2018.6.11"),
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.side_effect = StorageError

        # test
        res1, status, res2 = supercede(new_rel.e_print.arxiv_id,
                                       new_rel.e_print.version,
                                       prev_rel.identifier,
                                       new_rel.resource.resource_type,
                                       new_rel.resource.identifier,
                                       new_rel.description,
                                       "new tester")
        self.assertDictEqual(res1, {})
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertDictEqual(res2, {"error": "An error occured in storage"})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_suppress_with_success(self,
                                   mock_create: Any,
                                   mock_from_id: Any) -> None:
        """:func:`.suppress` gets a relation."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.return_value = prev_rel
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.SUPPRESS,
                           e_print=prev_rel.e_print,
                           resource=prev_rel.resource,
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.return_value = new_rel

        # test
        res1, status, res2 = suppress(new_rel.e_print.arxiv_id,
                                      new_rel.e_print.version,
                                      prev_rel.identifier,
                                      new_rel.description,
                                      "new tester")
        self.assertDictEqual(res1,
                             {new_rel.identifier: 
                              json.dumps(new_rel, default=support_json_default)})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertDictEqual(res2, {"previous": prev_rel.identifier})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_suppress_with_fail1(self,
                                 mock_create: Any,
                                 mock_from_id: Any) -> None:
        """:func:`.suppress` fails to find the previous relation."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.side_effect = NotFoundError
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.SUPPRESS,
                           e_print=prev_rel.e_print,
                           resource=prev_rel.resource,
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.return_value = new_rel

        # test
        res1, status, res2 = suppress(new_rel.e_print.arxiv_id,
                                      new_rel.e_print.version,
                                      prev_rel.identifier,
                                      new_rel.description,
                                      "new tester")
        self.assertDictEqual(res1, {})
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertDictEqual(res2, {"error": "The previous relation cannot be found"})

    @mock.patch('relations.controllers.from_id')
    @mock.patch('relations.controllers.create')
    def test_suppress_with_fail2(self,
                                 mock_create: Any,
                                 mock_from_id: Any) -> None:
        """:func:`.suppress` fails in storage."""
        prev_rel = Relation(identifier="123",
                            relation_type=RelationType.ADD,
                            e_print=EPrint(arxiv_id="1234.56789",
                                           version=3),
                            resource=Resource(resource_type="DOI",
                                              identifier="10.1023/hoge.2013.7.24"),
                            description="prev",
                            added_at=datetime(2019, 7, 1),
                            creator="old tester",
                            supercedes_or_suppresses=None)
        mock_from_id.return_value = prev_rel
        new_rel = Relation(identifier="158",
                           relation_type=RelationType.SUPPRESS,
                           e_print=prev_rel.e_print,
                           resource=prev_rel.resource,
                           description="new",
                           added_at=datetime(2019, 7, 3),
                           creator="new tester",
                           supercedes_or_suppresses=prev_rel.identifier)
        mock_create.side_effect = StorageError

        # test
        res1, status, res2 = suppress(new_rel.e_print.arxiv_id,
                                      new_rel.e_print.version,
                                      prev_rel.identifier,
                                      new_rel.description,
                                      "new tester")
        self.assertDictEqual(res1, {})
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertDictEqual(res2, {"error": "An error occured in storage"})
