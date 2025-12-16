import sqlite3
import uuid
from domain.catalog import Track

DB_NAME = 'music_platform.db'

class TrackService:
    def get_all_tracks(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM songs')
            rows = cursor.fetchall()
            # Мапимо дані з БД у прості словники (DTO)
            return [dict(row) for row in rows]

    def get_track_by_id(self, track_id):
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM songs WHERE id = ?', (track_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def create_track(self, title, artist, uploader_id, filename="default.mp3"):
        # Використовуємо Domain модель для створення
        # Тут ми могли б додати бізнес-перевірки (наприклад, цензуру назви)
        new_track = Track(
            title=title,
            artist=artist,
            uploader_id=uuid.UUID(uploader_id) if isinstance(uploader_id, str) else uploader_id,
            filename=filename
        )

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # У реальному проєкті тут краще використати Repository Pattern, але поки SQL тут
            cursor.execute('''
                INSERT INTO songs (title, artist, uploader, filename, is_visible)
                VALUES (?, ?, ?, ?, ?)
            ''', (new_track.title, new_track.artist, str(new_track.uploader_id), new_track.filename, 1))
            
            # Повертаємо ID новоствореного запису (або об'єкт)
            return {
                "id": cursor.lastrowid, # SQLite повертає int ID, хоча в DDD ми хотіли UUID. Для сумісності з БД поки int.
                "title": new_track.title,
                "artist": new_track.artist
            }

    def delete_track(self, track_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM songs WHERE id = ?', (track_id,))
            return cursor.rowcount > 0