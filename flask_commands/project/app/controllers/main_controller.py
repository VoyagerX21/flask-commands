from flask import render_template

class MainController:
    @staticmethod
    def index() -> str:
        return render_template('mains/index.html')
