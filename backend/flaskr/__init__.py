import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# utility for paginating questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)# default page to 1
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #DONE
  CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
      '''
      Sets access control.
      '''
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #DONE
  @app.route('/categories')
  def get_categories():

    # first it gets all categories and add them to list
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type

    # if no categories found, then abort with 404
    if (len(categories_dict) == 0):
        abort(404)

    # Otherwise, return requested Data
    return jsonify({
        'success': True,
        'categories': categories_dict
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories.
   

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  #DONE
  @app.route('/questions')
  def get_questions():
      

    # query all questions then paginate them
    selection = Question.query.all()
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)

    # first it gets all categories and add them to dictionary
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type

    # if no categories found, then abort with 404
    if (len(current_questions) == 0):
        abort(404)

    # Otherwise, return requested Data
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': categories_dict
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  #DONE
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
      try:
          # get the question by id
          question = Question.query.filter_by(id=id).one_or_none()

          # abort 404 if no question found
          if question is None:
              abort(404)

          # delete the question
          question.delete()
  
          # return success response
          return jsonify({
              'success': True,
              'deleted': id
          })

      except:
          # if not delted, then abort with 422
          abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():

      # get request body
      body = request.get_json()

      # if it contains search term

      if (body.get('searchTerm')):
          search_term = body.get('searchTerm')#fetch it

          # query the database using search term
          selection = Question.query.filter(
              Question.question.ilike(f'%{search_term}%')).all()# use ilike for case insensitive lookup

          # if no results found, then abort with 404
          if (len(selection) == 0):
                abort(404)

          # paginate the results
          paginated = paginate_questions(request, selection)

          # return results
          return jsonify({
              'success': True,
              'questions': paginated,
              'total_questions': len(Question.query.all())
          })

      # if no search term, create new question
      else:
          # load data from body
          new_question = body.get('question')
          new_answer = body.get('answer')
          new_difficulty = body.get('difficulty')
          new_category = body.get('category')

          # ensure all fields have data
          if ((new_question is None) or (new_answer is None)
                  or (new_difficulty is None) or (new_category is None)):
              abort(422)

          try:
              # create and insert new question
              question = Question(question=new_question, answer=new_answer,
                                  difficulty=new_difficulty, category=new_category)
              question.insert()

              # get all questions and paginate
              selection = Question.query.order_by(Question.id).all()
              current_questions = paginate_questions(request, selection)

              # return data to view
              return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

          except:
                # if no unprocessable, then abort with 422
              abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):


      # get the category by id
      category = Category.query.filter_by(id=id).one_or_none()

      # if no unprocessable, then abort with 404
      if (category is None):
            abort(400)

      # look for matching questions
      selection = Question.query.filter_by(category=category.id).all()

      # paginate the selection
      paginated = paginate_questions(request, selection)

      # return the results
      return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
      })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    