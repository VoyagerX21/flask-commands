from flask import render_template

class MainController:
    def index(self) -> str:
        return render_template('mains/index.html')
