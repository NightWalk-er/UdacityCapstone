import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, Movie, Actor, db
from auth import AuthError, requires_auth

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
    movie_names = [m.format() for m in movies]

    if len(movie_names) == 0:
      abort(404)

    for movie in movie_names:
      movie['actors'] = [actor.format() for actor in movie['actors']]

    message = {
        'success': True,
        'movies': movie_names,
        'total movies': len(movie_names)
      }

    return jsonify(message)

  @app.route('/movies/create', methods=['POST'])
  @requires_auth('post:movie')
  def post_new_movie(token):
    body = request.get_json()

    try:
      title = body.get('title', None)
      release_date = body.get('release_date', None)

      if not title:
        abort(422)

      movie = Movie(title=title, release_date=release_date)
      movie.insert()
      new_movie = Movie.query.get(movie.id)
      new_movie = new_movie.format()

      return jsonify({
        'success': True,
        'created': movie.id,
        'new_movie': new_movie
      })
    
    except:
      abort(400)

  
  @app.route('/movies/delete/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movie')
  def delete_movie(token, movie_id):
    try:
      del_movie = Movie.query.filter(Movie.id == movie_id).one_or_more()

      if del_movie is None:
        abort(404)

      db.session.commit()
      db.session.close()
      return jsonify({
        "success": True,
        "movie id deletd": movie_id, # displaying id of deleted movie
        "message" : "Delete occured",
        "total movies": len(Movie.query.all())
      })
    except:
      abort(422)


  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(token):
    actors = Actor.query.all()
    actor_names = [actor.format() for actor in actors]
      
    if len(actor_names) == 0:
      abort(404)
      
    return jsonify({
      'success': True,
      'Actors':actor_names,
      'Total actors': len(Actor.query.all())
    })

  @app.route('/actors/create', methods=['POST'])
  @requires_auth('post:actor')
  def post_new_actor(token):
    body = request.get_json()
    try:
      name = body.get('name', None)
      age = body.get('age', None)

      if not name or not age:
        abort(422)

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
    except:
      abort(400,{"message":"JSON body required"})

  @app.route('/actors/delete/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actor')
  def delete_actor(token, actor_id):
    try:
      del_actor = Actor.query.filter(Actor.id == actor_id).one_or_more()
      if del_actor is None:
        abort(404)

      db.session.commit()
      db.session.close()
      return jsonify({
        "success": True,
        "message" : "Delete occured",
        "id" : actor_id, # displaying id of actor whose data is deleted 
        "Total Actor Remaining": len(Actor.query.all())
      })
    except:
      abort(422)

  @app.route('/actors/patch/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def patch_actor(token, actor_id):
    body = request.get_json()
    try:
      actor = Actor.query.filter(Actor.id == actor_id)
      if not actor:
        abort(404,{'message':'id {} not found'.format(actor_id)})

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
        "total actors": len(Actor.query.all())
      })
    except:
      abort(400,{"message":"either body is missing or actor's id is misssing"})
      
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