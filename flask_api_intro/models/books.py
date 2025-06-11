import os
import json
from flask import Blueprint, request, jsonify
from flask_api_intro.models import db

class Book(db.Model):
    """Model for Book."""
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(150), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    published_date = db.Column(db.Date(), nullable=True)

    @property
    def to_dict(self):
        """Convert the Book instance to a dictionary."""
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'published_date': self.published_date
        }