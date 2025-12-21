from app.controllers import MainController

from app.routes.posts import bp
@bp.route('/', methods=['GET'])def index():    return MainController.index()
@bp.route('/', methods=['GET'])def index():    return PostController.index()
