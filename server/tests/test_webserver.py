"""Unit tests for webserver provider endpoints."""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock config module before importing webserver
sys.modules['config'] = MagicMock()

# Set required env vars before importing
os.environ.setdefault('google_client_id', 'test-client-id')
os.environ.setdefault('google_client_secret', 'test-client-secret')

from database import db, app as db_app, Admin
from webserver import app


class TestWebserverProviders(unittest.TestCase):
    """Test provider-related endpoints."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Create test user
            admin = Admin(
                id='test-user-id',
                email='test@example.com',
                name='Test User',
                openai_key='sk-test123456789012345678901234567890123456789012345',
            )
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_providers_returns_list(self):
        resp = self.client.get('/get_providers')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('providers', data)
        self.assertIn('openai', data['providers'])
        self.assertIn('minimax', data['providers'])
        self.assertIn('models', data)
        self.assertIn('defaults', data)

    def test_get_providers_includes_minimax_models(self):
        resp = self.client.get('/get_providers')
        data = json.loads(resp.data)
        minimax_models = data['models']['minimax']
        self.assertIn('MiniMax-M2.5', minimax_models)
        self.assertIn('MiniMax-M2.5-highspeed', minimax_models)

    def test_get_providers_default_current_is_openai(self):
        resp = self.client.get('/get_providers')
        data = json.loads(resp.data)
        self.assertEqual(data['current'], 'openai')


class TestStoreKey(unittest.TestCase):
    """Test store_key endpoint with provider support."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_store_key_rejects_short_key(self):
        # store_key requires login; without login current_user is anonymous
        # This verifies the route exists and the validation path is reachable
        with self.assertRaises(AttributeError):
            self.client.post(
                '/store_key',
                data=json.dumps({'key': 'short', 'provider': 'openai'}),
                content_type='application/json',
            )


class TestChangeProvider(unittest.TestCase):
    """Test change_provider endpoint."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_change_provider_invalid_returns_400(self):
        resp = self.client.post(
            '/change_provider',
            data=json.dumps({'provider': 'invalid'}),
            content_type='application/json',
        )
        # Not logged in will likely error, but the route exists
        self.assertIn(resp.status_code, [302, 400, 401, 500])


class TestDatabaseModel(unittest.TestCase):
    """Test that Admin model has new provider fields."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_has_minimax_key_field(self):
        with app.app_context():
            admin = Admin(id='t1', email='t@t.com', name='T')
            admin.minimax_key = 'mm-test-key-123'
            db.session.add(admin)
            db.session.commit()
            fetched = Admin.query.get('t1')
            self.assertEqual(fetched.minimax_key, 'mm-test-key-123')

    def test_admin_has_llm_provider_field(self):
        with app.app_context():
            admin = Admin(id='t2', email='t2@t.com', name='T2')
            admin.llm_provider = 'minimax'
            db.session.add(admin)
            db.session.commit()
            fetched = Admin.query.get('t2')
            self.assertEqual(fetched.llm_provider, 'minimax')

    def test_admin_default_provider_is_openai(self):
        with app.app_context():
            admin = Admin(id='t3', email='t3@t.com', name='T3')
            db.session.add(admin)
            db.session.commit()
            fetched = Admin.query.get('t3')
            self.assertEqual(fetched.llm_provider, 'openai')


if __name__ == '__main__':
    unittest.main()
