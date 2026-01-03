from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.database import get_mongodb
import os
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv', 'json', 'log'}
UPLOAD_FOLDER = 'data/uploads'

def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['GET'])
@login_required
def upload_page():
    """Page d'upload"""
    return render_template('upload.html')

@upload_bp.route('/file', methods=['POST'])
@login_required
def upload_file():
    """Endpoint pour uploader un fichier"""
    try:
        # Vérifier qu'un fichier est présent
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400
        
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Créer le dossier si nécessaire
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Sauvegarder le fichier
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Obtenir les métadonnées
        file_size = os.path.getsize(filepath)
        
        # Enregistrer dans MongoDB
        mongo = get_mongodb()
        file_metadata = {
            'filename': filename,
            'original_filename': file.filename,
            'upload_date': datetime.now(),
            'size': file_size,
            'status': 'uploaded',
            'filepath': filepath,
            'records_count': 0,  # Sera mis à jour après traitement
            'uploaded_by': current_user.username
        }
        
        result = mongo.uploaded_files.insert_one(file_metadata)
        file_metadata['_id'] = str(result.inserted_id)
        
        # Convertir la date pour JSON
        file_metadata['upload_date'] = file_metadata['upload_date'].isoformat()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_metadata
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/status/<file_id>', methods=['GET'])
def get_upload_status(file_id):
    """Vérifier le statut d'un fichier uploadé"""
    try:
        from bson.objectid import ObjectId
        mongo = get_mongodb()
        
        file_doc = mongo.uploaded_files.find_one({'_id': ObjectId(file_id)})
        
        if not file_doc:
            return jsonify({'error': 'File not found'}), 404
        
        file_doc['_id'] = str(file_doc['_id'])
        if 'upload_date' in file_doc:
            file_doc['upload_date'] = file_doc['upload_date'].isoformat()
        
        return jsonify(file_doc), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
