from flask import Blueprint, send_from_directory
import os

# Define o caminho absoluto da pasta 'build'
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../build'))

# Cria o blueprint com a pasta estática correta
views_bp = Blueprint('views', __name__, static_folder=root_dir)

# Rota principal e fallback para SPA
@views_bp.route('/', defaults={'path': ''})
@views_bp.route('/<path:path>')
def serve(path):
    file_path = os.path.join(root_dir, path)

    if path != "" and os.path.exists(file_path):
        return send_from_directory(root_dir, path)
    else:
        return send_from_directory(root_dir, 'index.html')
