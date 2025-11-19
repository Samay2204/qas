import os
from flask import Flask, render_template


def create_app(test_config=None):
    # create flask instance inside the function
    app = Flask(__name__, instance_relative_config=True)

    # default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        # max upload size (16 MB)
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        # service account key (relative to package root). Put sa.json at project root or change path.
        SERVICE_ACCOUNT_FILE=os.path.abspath(os.path.join(app.root_path, '..', 'sa.json')),
        # optional: set this to the Drive folder id you shared with the service account
        DRIVE_PARENT_FOLDER_ID="13ri9alNYUCDpWmEvQIPyK-2dgiLOTLCf",
        # allowed file extensions for uploads
        ALLOWED_EXTENSIONS={'pdf', 'docx', 'txt'},
    )

  

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # register extensions / initialize components
    from . import db
    db.init_app(app)

    # register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import chatbot
    app.register_blueprint(chatbot.bp)

    from . import upload
    app.register_blueprint(upload.bp)

    @app.route('/')
    def home():
        return render_template('base.html')

    return app
