from flask import Blueprint, request, jsonify
from sqlalchemy.inspection import inspect
from flask_api_intro.models import db
from flask_api_intro.models.books import Book

bp_books = Blueprint('books', __name__)

@bp_books.route('/books', methods=['GET'])
def get_books():
    """Endpoint to retrieve all books."""
    # Retrieving all the books from the database
    books = Book.query.all()
    # Serializing objects so that we can send them in a JSON object
    serialized_books = [book.to_dict for book in books]
    # Sending all books back to the client in JSON object
    return jsonify(serialized_books)

@bp_books.route('/books/<string:isbn>', methods=['GET', 'POST'])
def add_book(isbn):
   # GET request for getting all books from DB
   if request.method == "GET":
       # retreiving all the books from DB
       books = Book.query.filter_by(isbn=isbn).all()
       # serializing objects so that we can send them in a JSON object
       serialized_books = [book.to_dict for book in books]
       # sending all books back to the client in JSON object
       return jsonify(serialized_books)

    # POST request for adding book to DB
   if request.method == "POST":
       # Getting user-passed data
       payload = request.get_json()

       # Creating a book object
       book = Book(isbn=payload['isbn'],
                   title=payload['title'],
                   author=payload['author'],
                   published_date=payload.get('published_date'))

       # add new book object to DB
       db.session.add(book)

       # commit db to save changes
       db.session.commit()

       # return the same book to let the user know that it has been added to the DB
       return jsonify(json.dumps(payload))