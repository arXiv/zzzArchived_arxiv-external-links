"""Tests for :mod:`routes.api`."""

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
from relations.factory import create_api_app
from .. import api

class TestExternalAPIRoutes(TestCase):
    """Sample tests for external API routes."""

    def setUp(self) -> None:
        """Initialize the Flask application, and get a client for testing."""
        os.environ['JWT_SECRET'] = 'foosecret'
        self.app = create_api_app()
        self.client = self.app.test_client()

    @mock.patch(f'{api.__name__}.controllers.create_new')
    def test_create_new(self, mock_create_new: Any) -> None:
        """Endpoint /api/<string:arxiv_id_str>v<int:arxiv_ver>/relations returns JSON about the newly created relation."""

        post_data = {'resource_type':'type',
                    'resource_id':1012,
                    'description':'test relation',
                    'creator':'tester'}
        return_data={'relation_values':'vals'}
        mock_create_new.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.post('/api/TESTv10/relations',
                                    data=json.dumps(post_data),
                                    headers={'Authorization':token},
                                    content_type='application/json')

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)

    @mock.patch(f'{api.__name__}.controllers.supercede')
    def test_supercede(self, mock_supercede: Any) -> None:
        """Endpoint /api/<string:arxiv_id_str>v<int:arxiv_ver>/relations/<string:relation_id_str> returns JSON about the newly created relation and the relation it superceded."""

        post_data = {'resource_type':'type',
                    'resource_id':1012,
                    'description':'test relation',
                    'creator':'tester'}
        return_data={'relation_values':'vals'}
        mock_supercede.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.put('/api/TESTv10/relations/relation1',
                                    data=json.dumps(post_data),
                                    headers={'Authorization':token},
                                    content_type='application/json')

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)

    @mock.patch(f'{api.__name__}.controllers.suppress')
    def test_suppress(self, mock_suppress: Any) -> None:
        """Endpoint /api/<string:arxiv_id_str>v<int:arxiv_ver>/relations/<string:relation_id_str> returns JSON about the newly created relation and the relation it suppressed."""

        post_data = {'resource_type':'type',
                    'resource_id':1012,
                    'description':'test relation',
                    'creator':'tester'}
        return_data={'relation_values':'vals'}
        mock_suppress.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.delete('/api/TESTv10/relations/relation1',
                                    data=json.dumps(post_data),
                                    headers={'Authorization':token},
                                    content_type='application/json')

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)


    @mock.patch(f'{api.__name__}.controllers.get_relations')
    def test_get_relations(self, mock_get_relations: Any) -> None:
        """Endpoint /api/<string:arxiv_id_str>v<int:arxiv_ver> returns JSON about all relations belonging to an id."""

        return_data = {'relation1':{'description':''},'relation2':{'description':''}}
        mock_get_relations.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.get('/api/TESTv1',headers={'Authorization':token})

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)


    @mock.patch(f'{api.__name__}.controllers.get_events')
    def test_get_events(self, mock_get_events: Any) -> None:
        """Endpoint /api/<string:arxiv_id_str>v<int:arxiv_ver>/log returns JSON about all events belonging to an id."""

        return_data = {'event1':{'description':''},'event1':{'description':''}}
        mock_get_relations.return_value = return_data, HTTPStatus.OK, {}
        token = generate_token('1234', 'foo@user.com', 'foouser',
                               scope=[])
        response = self.client.get('/api/TESTv1/log',headers={'Authorization':token})

        expected_data = return_data

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(json.loads(response.data), expected_data)

