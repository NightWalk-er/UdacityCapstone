import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, Movie, Actor, db
from auth import AuthError, requires_auth
#from config import pagination

#pages = pagination['pages']

## creating and configuring our app
def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

  @app.after_request
  def after_request(response):
    # Adding access headers
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
      response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
      return response
  
  @app.route('/movies')
  @requires_auth('get:movies')
  def get_movies(token):
      movies = Movie.query.all()
      movie_names = [movie.format() for movie in movies]

      if len(movie_names) == 0:
        abort(404,{'message':'No movie found in database'})

      for movie in movie_names:
        movie['actors'] = [i.format() for i in movie_names['actors']]
      return jsonify({
        'success': True,
        'movies': movie_names
      })
  
  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(token):
      actors = Actor.query.all()
      actor_names = [actor.format() for actor in actors]
      
      if len(actor_names) == 0:
        abort(404,{'message':'No actor found in database'})
      
      return jsonify({
        'success': True,
        'Actors':actor_names
      })

  @app.route('/movies/create', methods=['POST'])
  @requires_auth('post:movie')
  def post_new_movie(token):
      body = request.get_json()

      if not body:
        abort(400,{'message':'Require JSON body does not exist'})

      title = body.get('title', None)
      release_date = body.get('release_date', None)

      if not title:
        abort(422,{'message':'No title given'})

      movie = Movie(title=title, release_date=release_date)
      movie.insert()
      new_movie = Movie.query.get(movie.id)
      new_movie = new_movie.format()

      return jsonify({
        'success': True,
        'created': movie.id,
        'new_movie': new_movie
      })

  @app.route('/actors/create', methods=['POST'])
  @requires_auth('post:actor')
  def post_new_actor(token):
      body = request.get_json()

      if not body:
        abort(400,{'message':'request does not contain a valid JSON body'})
      
      name = body.get('name', None)
      age = body.get('age', None)

      if not name:
      abort(422, {'message': 'no name provided.'})

      if not age:
      abort(422, {'message': 'no age provided.'})

      gender = body.get('gender', None)
      movie_id = body.get('movie_id', None)

      actor = Actor(name=name, age=age, gender=gender, movie_id=movie_id)
      actor.insert()
      new_actor = Actor.query.get(actor.id)
      new_actor = new_actor.format()

      return jsonify({
        'success': True,
        'created': actor.id,
        'new_actor': new_actor
      })

  @app.route('/movies/delete/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movie')
  def delete_movie(token, movie_id):

      if not movie_id:
        abort(400,{'message':'Append a movie id'})

      movie_to_be_deleted=Movie.query.filter(Movie.id == movie_id).one_or_more()

      if not movie_to_be_deleted:
        abort(404,{'message':'id {} not found'.format(movie_id)})

      db.session.commit()
      db.session.close()
      return jsonify({
        "success": True,
        "message" : "Delete occured"
      })

  @app.route('/actors/delete/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actor')
  def delete_actor(token, actor_id):

      if not actor_id:
        abort(400,{'message':'Append a actor id'})

      actor_to_delete = Actor.query.filter(Actor.id == actor_id).one_or_more()
      if not actor_to_delete:
        abort(404,{'message':'id {} not found'.format(actor_id)})

      db.session.commit()
      db.session.close()
      return jsonify({
        "success": True,
        "message" : "Delete occured"
      })

  @app.route('/actors/patch/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def patch_actor(toekn, actor_id):
      body = request.get_json()

      if not actor_id:
        abort(400,{'message':'Append an actor'})
      if not body:
        abort(400,{'message':'Does not have valid JSON body'})

      actor = Actor.query.filter(Actor.id == actor_id)
      if not actor:
        abort(404,{'message':'Actor with id {} not found in database'.format(actor_id)})

      name = body.get('name', None)
      age = body.get('age', None)
      gender = body.get('gender', None)
      movie_id = body.get('movie_id', None)

      # adding new actor

      actor.name = name
      actor.age = age
      actor.gender = gender
      actor.movie_id = movie_id

      actor.update()

      return jsonify({
        "success": True,
        "message": "update occured"
      })
    
  @app.route('/movies/patch/<int:movie_id>')
  @requires_auth('patch:movies')
  def patch_movie(token, movie_id):
      
      body = request.get_json()
      if not body:
        abort(400,{'message':'No JSON body associated'})

      movie = Movie.query.filter(Movie.id == movie_id)
      if not body:
        abort(404,{'message':'Movie id {} not found'.format(movie_id)})
      
      title = body.get('title', None)
      release_date = body.get('release_date', None)
      movie.title = title
      movie.release_date = release_date
      movie.update()
      return jsonify({
        "success": True,
        "message": "update occured"
      })
      
  ## Error Handlers

  @app.errorhandler(AuthError)
  def failed_authorization(error):
      return jsonify({
        'success': False,
        'error': AuthError.status_code,
        'message': AuthError.error['description']
      }), AuthError.status_code

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        'success': False,
        'error' : 404,
        'message' : 'Not Found'
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable'
      }), 422


  return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)