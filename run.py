from flask import Flask
import os
from app.api.main import api_bp
from app.views.main import views_bp

app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(views_bp)

if __name__ == '__main__':
    os.makedirs('memorias', exist_ok=True)
    app.run(host='0.0.0.0', port=5005, debug=True)
