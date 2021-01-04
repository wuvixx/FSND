import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response


@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        q = Category.query.all()
        if len(q) == 0:
            abort(404)
        data = {'success': True, 'categories': {}}
        for category in q:
            data['categories'][category.id] = category.type
    except:
        abort(500)
    return data


@app.route('/questions', methods=['GET'])
def get_questions():
    try:
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories_q = Category.query.order_by(Category.id).all()
        categories = {}
        for category in categories_q:
            categories[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)
        except:
            abort(500)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'categories': categories,
        'currentCategory': None
      })


@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    q = Question.query.filter_by(id=question_id).one_or_none()
    if q is None:
        abort(422)
    Question.delete(q)
    return jsonify({'success': True, 'question': q.id})


@app.route('/questions', methods=['POST'])
def add_question():
    try:
        request_json = request.get_json()
        new_question = Question(question=request_json['question'],
                                answer=request_json['answer'],
                                category=request_json['category'],
                                difficulty=request_json['difficulty'])
        Question.insert(new_question)
    except:
        abort(422)

    return jsonify({'success': True, 'question': new_question.id})


@app.route('/questions/search', methods=['POST'])
def search_question():
    try:
        term = request.get_json()['searchTerm']
        q = Question.query.filter(Question.question.ilike(f'%{term}%')).\
            order_by(Question.id).all()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'questions': [question.format() for question in q],
        'total_questions': len(q)
    })


@app.route('/categories/<int:category_id>/questions', methods=['GET'])
def get_questions_by_category(category_id):
    try:
        q = Question.query.filter_by(category=str(category_id)).all()
        if len(q) == 0:
            abort(404)
    except:
        abort(500)

    return jsonify({
        'success': True,
        'questions': [question.format() for question in q],
        'total_questions': len(q)
    })


@app.route('/quizzes', methods=['POST'])
def get_quizzes_by_category():
    try:
        request_json = request.get_json()
        previous_questions = request_json['previous_questions']
        chosen_category = request_json['quiz_category']['id']
        q = None
        r = None
        if chosen_category != 0:
            q = Question.query.filter((Question.category == chosen_category) &
                                      (~Question.id.in_(previous_questions))).\
                                      order_by(Question.id).all()
        else:
            q = Question.query.filter(~Question.id.in_(previous_questions)).\
                                      order_by(Question.id).all()
        if q:
            r = random.choice(q)
    except:
        abort(422)

    return jsonify({'success': True, 'question': r.format() if r else None})


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'server error'
    }), 500


return app
