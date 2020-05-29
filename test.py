import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Actor, Movie, setup_db
from app import create_app
from models import db
from bearer_conf import bearer_tokens
from datetime import date

class DeployTestCase(unittest.TestCase):

    def setUp(self):
        '''defining test variables and initializing app'''
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db.drop_all()
        db.create_all()

        self.new_actor = { 
            'name' : 'Maria',
            'age' : 19,
            'gender': 'female'
        }

        self.json_create_movie = {
            'title' : 'DayDreams Movie',
            'release_date' : date.today()
        }

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
        res = self.client().post('/actors', json = self.new_actor , headers = bearer_tokens['casting_director'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertEqual(json.loads(res.data)['created'], 2)

    def test_error_unable_create_new_actor(self):
        res = self.client().post('/actors', json = self.new_actor)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'unauthorized')

    def test_no_name_actor(self):
        res = self.client().post('/actors', json = { "age":30 }, headers = bearer_tokens['casting_director'])

        self.assertEqual(res.status_code, 422)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'unprocessable')

    def test_change_actor_details(self):
        res = self.client().patch('/actors/1', json = {'age': 30}, headers = bearer_tokens['casting_director'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertTrue(len(json.loads(res.data)['actor']) > 0)
        self.assertEqual(json.loads(res.data)['updated'], 1)

    def test_invalid_body_edit_actor(self):
            res = self.client().patch('/actors/100000', headers = bearer_tokens['casting_director'])

            self.assertEqual(res.status_code, 400)
            self.assertFalse(json.loads(res.data)['success'], False)
            self.assertEqual(json.loads(res.data)['message'] , 'bad request ')

    def test_error_404_edit_actor(self):
        res = self.client().patch('/actors/100000', json = {'age' : 30}, headers = bearer_tokens['casting_director'])
        
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'] , 'not found')

    def test_missing_header_delete_actor(self):
        res = self.client().delete('/actors/1')

        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'unauthorized')

    def test_permission_denied_delete_actor(self):
        res = self.client().delete('/actors/1', headers = bearer_tokens['casting_assistant'])

        self.assertEqual(res.status_code, 403)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'no permission')

    def test_success_delete_actor(self):
        res = self.client().delete('/actors/1', headers = bearer_tokens['casting_director'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertEqual(json.loads(res.data)['deleted'], '1')

    def test_not_found_delete_actor(self):
        res = self.client().delete('/actors/100000', headers = bearer_tokens['casting_director'])

        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'] , 'not found')

    def test_create_new_movie(self):
        res = self.client().post('/movies', json = self.json_create_movie, headers = bearer_tokens['executive_producer'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertEqual(json.loads(res.data)['created'], 2)

    def test_no_name_create_new_movie(self):
        res = self.client().post('/movies', json = {
            'release_date' : date.today()
        }, headers = bearer_tokens['executive_producer'])

        self.assertEqual(res.status_code, 422)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'unprocessable')

    def test_edit_movie(self):
        res = self.client().patch('/movies/1', json = {'release_date' : date.today()}, headers = bearer_tokens['executive_producer'])
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertTrue(len(json.loads(res.data)['movie']) > 0)

    def test_invalid_b_edit_movie(self):
        res = self.client().patch('/movies/1', headers = bearer_tokens['executive_producer'])
        
        self.assertEqual(res.status_code, 400)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'] , 'bad request')

    def test_not_found_edit_movie(self):
        res = self.client().patch('/movies/100000', json = {'release_date' : date.today()}, headers = bearer_tokens['executive_producer'])
       
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'] , 'not found')

    def test_header_missing_delete_movie(self):
        res = self.client().delete('/movies/1')
        
        self.assertEqual(res.status_code, 401)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'unauthorized')

    def test_permission_denied_delete_movie(self):
        res = self.client().delete('/movies/1', headers = bearer_tokens['casting_assistant'])
        
        self.assertEqual(res.status_code, 403)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'], 'Permission not found.')

    def test_success_delete_movie(self):
        res = self.client().delete('/movies/1', headers = bearer_tokens['executive_producer'])
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'], True)
        self.assertEqual(json.loads(res.data)['deleted'], '1')

    def test_not_found_delete_movie(self):
        res = self.client().delete('/movies/100000', headers = bearer_tokens['executive_producer'])
        
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json.loads(res.data)['success'], False)
        self.assertEqual(json.loads(res.data)['message'] , 'not found')

if __name__ == "__main__":
    unittest.main()
