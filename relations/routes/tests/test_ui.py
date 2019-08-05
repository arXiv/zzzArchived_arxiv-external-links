"""Tests for :mod:`routes.ui`."""

import json
import os
from http import HTTPStatus
from typing import Any, Optional
from unittest import TestCase, mock
from datetime import datetime

import jsonschema
from flask import Flask

from arxiv.users.helpers import generate_token
from arxiv.users import auth
from arxiv.users.domain import Scope
from relations.factory import create_ui_app
from .. import ui


class TestUIRoutes(TestCase):
    """tests for UI routes."""

    def setUp(self) -> None:
        """Initialize the Flask application, and get a client for testing."""
        os.environ['JWT_SECRET'] = 'foosecret'
        self.app = create_ui_app()
        self.client = self.app.test_client()

    @mock.patch(f'{ui.__name__}.controllers.create_new')
    def test_create_new(self, mock_create_new: Any) -> None:
        """Endpoint /<string:arxiv_id_str>v<int:arxiv_ver>/relations returns html about the newly created relation."""
        post_data = {'resource_type': 'type',
                     'resource_id': 1012,
                     'description': 'test relation',
                     'creator': 'tester'}
        return_data = {'arxiv_id': 'TEST',
                       'arxiv_ver': 10,
                       'resource_type': 'type',
                       'description': 'test relation'}
        mock_create_new.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.post('/TESTv10/relations',
                                    data=json.dumps(post_data),
                                    headers={'Authorization': token},
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch(f'{ui.__name__}.controllers.supercede')
    def test_supercede(self, mock_supercede: Any) -> None:
        """Endpoint /<string:arxiv_id_str>v<int:arxiv_ver>/relations/<string:relation_id_str> returns html about the newly created relation and the relation it superceded."""
        post_data = {'resource_type': 'type',
                     'resource_id': 1012,
                     'description': 'test relation',
                     'creator': 'tester'}
        return_data = {'arxiv_id': 'TEST',
                       'arxiv_ver': 10,
                       'relation_id': 1012,
                       'resource_type': 'type',
                       'description': 'test relation'}
        mock_supercede.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.post('/TESTv10/relations/relation1',
                                    data=json.dumps(post_data),
                                    headers={'Authorization': token},
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch(f'{ui.__name__}.controllers.suppress')
    def test_suppress(self, mock_suppress: Any) -> None:
        """Endpoint /<string:arxiv_id_str>v<int:arxiv_ver>/relations/<string:relation_id_str>/delete returns html about the newly created relation and the relation it suppressed."""
        post_data = {'resource_type': 'type',
                     'resource_id': 1012,
                     'description': 'test relation',
                     'creator': 'tester'}
        return_data = {'arxiv_id': 'TEST',
                       'arxiv_ver': 10,
                       'relation_id': 1012,
                       'resource_type': 'type',
                       'description': 'test relation'}
        mock_suppress.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.post('/TESTv10/relations/relation1/delete',
                                    data=json.dumps(post_data),
                                    headers={'Authorization': token},
                                    content_type='application/json')

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch(f'{ui.__name__}.controllers.retrieve')
    def test_get_relations(self, mock_retrieve: Any) -> None:
        """Endpoint /<string:arxiv_id_str>v<int:arxiv_ver> returns html about all relations belonging to an id."""
        return_data = {'relations': [{'key1': 'val1'}, {'key1': 'val2'}]}
        mock_retrieve.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.get('/TESTv1', headers={'Authorization': token})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')

    @mock.patch(f'{ui.__name__}.controllers.retrieve')
    def test_get_events(self, mock_retrieve: Any) -> None:
        """Endpoint /<string:arxiv_id_str>v<int:arxiv_ver>/log returns html about all events belonging to an id."""
        return_data = {'relations': [{'key1': 'val1'}, {'key1': 'val2'}]}
        mock_retrieve.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.get('/TESTv1/log', headers={'Authorization': token})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')
