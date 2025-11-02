import os

from flask import Flask

from flask import render_template


def create_app(test_config=None):
    # create flask instance inside the function
    # creating and configuring the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    @app.route('/')
    def home():
        return render_template('base.html')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import chatbot
    app.register_blueprint(chatbot.bp)

    return app