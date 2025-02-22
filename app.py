from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.ai_router import ai_routes
from routes.video_router import video_routes

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register routes
    app.register_blueprint(ai_routes, url_prefix='/api')
    app.register_blueprint(video_routes, url_prefix='/api')

    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Route not found'}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)