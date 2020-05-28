import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Actor, Movie, setup_db
from app import create_app
from models import db
import datetime

casting_assistant_auth_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

casting_director_auth_header = {
    'Authorization': bearer_tokens['casting_director']
}

executive_producer_auth_header = {
    'Authorization': bearer_tokens['executive_producer']
}

class CastingTestCase(unittest.TestCase):

    def setUp(self):
        '''defining test variables and initializing app'''
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db.drop_all()
        db.create_all()

    ''' if we wish to bind our app current context we can use the code below'''
        #with self.app.app_context():
        #   self.db = SQLAlchemy()
        #    self.db.init_app(self.app)
        #    self.db.drop_all()
        #    self.db.create_all()

    def tearDown(self):
        pass

    # testing the app

    def test_create_new_actor(self):
        res = self.client().post('/actors', json ={'name' : 'Crisso','age' : 25} , headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['created'], 2)

    def test_error_unable_create_new_actor(self):
        res = self.client().post('/actors', json = {'name' : 'Crisso','age' : 25})
        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'Authorization header is expected.')

    def test_no_name_actor(self):
        res = self.client().post('/actors', json = { "age":25 }, headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'no name provided.')

    def test_change_actor(self):
        res = self.client().patch('/actors/1', json = {'age': 30}, headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertTrue(len(json.loads(res.data)['actor']) > 0)
        self.assertEqual(json.loads(res.data)['updated'], 1)

    def test_invalid_body_edit_actor(self):
            res = self.client().patch('/actors/100000', headers = casting_director_auth_header)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(json.loads(res.data)['success'])
            self.assertEqual(json.loads(res.data)['message'] , 'request does not contain a valid JSON body.')

    def test_error_404_edit_actor(self):
        json_edit_actor_with_new_age = {
            'age' : 30
        }
        res = self.client().patch('/actors/100000', json = json_edit_actor_with_new_age, headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'] , 'Actor with id 100000 not found in database.')

    def test_missing_header_delete_actor(self):
        res = self.client().delete('/actors/1')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'Authorization header is expected.')

    def test_permission_denied_delete_actor(self):
        res = self.client().delete('/actors/1', headers = casting_assistant_auth_header)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'Permission not found.')

    def test_success_delete_actor(self):
        res = self.client().delete('/actors/1', headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['deleted'], '1')

    def test_not_found_delete_actor(self):
        res = self.client().delete('/actors/100000', headers = casting_director_auth_header)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'] , 'Actor with id 15125 not found in database.')

    def test_create_new_movie(self):
        json_create_movie = {
            'title' : 'Crisso Movie',
            'release_date' : date.today()
        }
        res = self.client().post('/movies', json = json_create_movie, headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['created'], 2)

    def test_no_name_create_new_movie(self):
        json_create_movie_without_name = {
            'release_date' : date.today()
        }
        res = self.client().post('/movies', json = json_create_movie_without_name, headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'no title provided.')

    def test_edit_movie(self):
        res = self.client().patch('/movies/1', json = {'release_date' : date.today()}, headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertTrue(len(json.loads(res.data)['movie']) > 0)

    def test_invalid_b_edit_movie(self):
        res = self.client().patch('/movies/1', headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'] , 'request does not contain a valid JSON body.')

    def test_not_found_edit_movie(self):
        res = self.client().patch('/movies/123412', json = {'release_date' : date.today()}, headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'] , 'Movie with id 123412 not found in database.')

    def test_header_missing_delete_movie(self):
        res = self.client().delete('/movies/1')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'Authorization header is expected.')

    def test_permission_denied_delete_movie(self):
        res = self.client().delete('/movies/1', headers = casting_assistant_auth_header)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'], 'Permission not found.')

    def test_success_delete_movie(self):
        res = self.client().delete('/movies/1', headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['deleted'], '1')

    def test_not_found_delete_movie(self):
        res = self.client().delete('/movies/100000', headers = executive_producer_auth_header)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'])
        self.assertEqual(json.loads(res.data)['message'] , 'Movie with id 100000 not found in database.')

if __name__ == "__main__":
    unittest.main()
