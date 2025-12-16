from flask import Blueprint, request, jsonify
from service.track_service import TrackService

# Створюємо Blueprint (модуль маршрутів)
tracks_bp = Blueprint('tracks', __name__, url_prefix='/api/tracks')
service = TrackService()

@tracks_bp.route('', methods=['GET'])
def list_tracks():
    tracks = service.get_all_tracks()
    return jsonify(tracks), 200

@tracks_bp.route('/<int:track_id>', methods=['GET'])
def get_track(track_id):
    track = service.get_track_by_id(track_id)
    if not track:
        return jsonify({"error": "Not Found", "message": "Track not found"}), 404
    return jsonify(track), 200

@tracks_bp.route('', methods=['POST'])
def create_track():
    data = request.get_json()
    
    # Проста валідація (DTO validation)
    if not data or 'title' not in data or 'artist' not in data:
        return jsonify({"error": "ValidationError", "message": "Title and artist are required"}), 400
    
    # Виклик сервісу
    try:
        # Для спрощення передаємо string як uploader_id
        new_track = service.create_track(
            title=data['title'],
            artist=data['artist'],
            uploader_id=data.get('uploader_id', 'anon'),
            filename=data.get('filename', 'default.mp3')
        )
        return jsonify(new_track), 201
    except Exception as e:
        return jsonify({"error": "InternalError", "message": str(e)}), 500

@tracks_bp.route('/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    success = service.delete_track(track_id)
    if not success:
        return jsonify({"error": "Not Found", "message": "Track not found"}), 404
    return '', 204