from flask import Blueprint

bp = Blueprint('posts', __name__)

from app.routes.posts import routes
