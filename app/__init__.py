#This is where we initialize the Flask app and register the blueprints (modular routes).

from flask import Flask
from app.routes.main_routes import process_bp
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
def create_app():
    # Initialize the Flask app
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    # Load other necessary environment variables
    app.config['BASE_URLS'] = os.getenv('BASE_URLS').split(',')
    app.config['DOCUMENT_LINK_BASE'] = os.getenv('DOCUMENT_LINK_BASE')
    app.config['USER_AGENT'] = os.getenv('USER_AGENT')  # Add user-agent from .env
    app.config['ALLOWED_PREFIXES'] = os.getenv('ALLOWED_PREFIXES').split(',')  # Load prefixes

    # Set up logging
    logging.basicConfig(level=logging.INFO)  # Set the logging level
    app.logger.info('Flask app initialized successfully.')
    # Register blueprints
    register_blueprints(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""    
    app.register_blueprint(process_bp)
    


