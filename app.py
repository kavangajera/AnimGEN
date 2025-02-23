from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes.ai_router import ai_routes

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register routes
    app.register_blueprint(ai_routes, url_prefix='/api')
    

    # Define the root route
    @app.route('/')
    def home():
        return jsonify({'message': 'Welcome to the ANIMGEN API'}), 200

    # Error handling
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Route not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, use_reloader=False)
