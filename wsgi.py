from app import app
from config import Config

if __name__ == "__main__":
    print(f"Starting production server on {Config.HOST}:{Config.PORT}")

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=False,
        threaded=True
    )