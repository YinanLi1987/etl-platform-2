#This is where we initialize the Flask app and register the blueprints (modular routes).

from flask import Flask
from app.folder_manager import create_required_folders
from pathlib import Path
def create_app():
    # Initialize the Flask app
    app = Flask(__name__)
     # Define the base path for the project
    base_path = Path(__file__).resolve().parent.parent

    # Create the necessary folders
    create_required_folders(base_path)

    app.config['PREPROCESSED_FOLDER'] = base_path / 'preprocessed'
    app.config['TEMP_FOLDER'] = base_path / 'temp'
    app.config['EXTRACTED01_FOLDER'] = base_path / 'extracted01'
    app.config['EXTRACTED02_FOLDER'] = base_path / 'extracted02'

    # Register blueprints
    register_blueprints(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.main_routes import process_bp 
    app.register_blueprint(process_bp)
    


