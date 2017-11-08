import os

from qrmobservium.common import logger

LOG = logger.Logger(__name__)

def create_app(config):

    from flask import Flask
    from qrmobservium.views import api_blueprint, ui_blueprint

    app = Flask(__name__, root_path=os.getcwd(), template_folder=os.getcwd())
    app.config.from_object(config)

    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(ui_blueprint, url_prefix='')

    return app
