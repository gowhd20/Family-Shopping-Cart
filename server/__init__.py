####################################
## Readable code versus less code ##
####################################

import logging as logger

from flask import current_app, Flask, redirect, Blueprint, Response
from flask_restful import Resource, Api

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)
    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logger.basicConfig(level=logger.INFO)

    # Setup the data model.
    with app.app_context():
        model = get_model()

    # Register the Bookshelf CRUD blueprint.
    from . import rest_main
    api = rest_main.init_restful()
    #from . import helloworld2

    app.register_blueprint(rest_main.ms, url_prefix='/ms')


    # Add a default root route.
    @app.route("/")
    def index():
    	#return Response(js, status=200, mimetype='application/json')
        return """ you have missed /ms in your url """, 404
    

    @app.errorhandler(500)
    def server_error(e):
	    return """
	    An internal error occurred: <pre>{}</pre>
	    See logs for full stacktrace.
	    """.format(e), 500

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'mongodb':
        from . import model_mongodb
        model = model_mongodb
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model
