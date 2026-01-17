from flask import Blueprint

bp = Blueprint('comments', __name__)

from app.routes.recipes.comments import routes
