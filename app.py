from flask import Flask
from flask_cors import CORS
from config import Config

from routes.stats import stats_bp
from routes.contests import contests_bp
from routes.profiles import profiles_bp
from routes.badges import badges_bp
from routes.docs import docs_bp

app = Flask(__name__)
CORS(app)

app.config.from_object(Config)

# Register blueprints
app.register_blueprint(stats_bp)
app.register_blueprint(contests_bp)
app.register_blueprint(profiles_bp)
app.register_blueprint(badges_bp)
app.register_blueprint(docs_bp)

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
