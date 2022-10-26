import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()
@app.after_request
def after_request(response):
    response.headers.add(
                'Allow-Control-Allow-Headers',
                'Content-Type,Authorization,true'
                )
    response.headers.add(
                'Allow-Control-Allow-Methods',
                'GET, POST, PATCH, DELETE, OPTIONS'
                )

    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [t.short() for t in drinks]
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    data = request.get_json()
    
    if data is None:
        abort(400)

    title = data.get('title', None)
    recipe = data.get('recipe', None)
    
    if (title is None) or (recipe is None):
        abort(400)

    if not isinstance(recipe, list):
        abort(422)

    drinks = Drink(title=title, recipe=json.dumps(recipe))
    
    try:
        drinks.insert()
    except Exception:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drinks.long()]
    }), 200





'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    
    data = request.get_json()
    drinks = Drink.query.filter(Drink.id == id).one_or_none()

    if not drinks:
        abort(404)

    try:
        title = data.get('title')
        recipe = data.get('recipe')
        if title:
            drinks.title = title

        if recipe:
            drinks.recipe = json.dumps(drinks['recipe'])

        drinks.update()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drinks.long()]}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drinks = Drink.query.filter(Drink.id == id).one_or_none()
    if not drinks:
        abort(404)
    try:
        drinks.delete()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''



  ############# Error  #############
    #################################

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        'error': 400,
        "message": "Bad request"
    }), 400

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        'error': 404,
        "message": "Page not found"
    }), 404

@app.errorhandler(422)
def unprocessable_recource(error):
    return jsonify({
        "success": False,
        'error': 422,
        "message": "Unprocessable recource"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        'error': 500,
        "message": "Internal server error"
    }), 500

@app.errorhandler(405)
def invalid_method(error):
    return jsonify({
        "success": False,
        'error': 405,
        "message": "Invalid method!"
    }), 405


