from flask import render_template

class PostController(object):
    @staticmethod
    def index() -> str:
        return render_template('posts/index.html')
