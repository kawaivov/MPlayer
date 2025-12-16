import os
import sqlite3
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Імпортуємо Blueprint (але ще не реєструємо!)
from api.tracks import tracks_bp

# 2. Створюємо додаток Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# 3. Налаштування
app.secret_key = 'super_secret_key_for_music_app'
DB_NAME = "music_platform.db"
UPLOAD_FOLDER_MUSIC = 'static/music'
UPLOAD_FOLDER_COVERS = 'static/covers'
ALLOWED_EXTENSIONS_MUSIC = {'mp3', 'wav', 'm4a'}
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER_MUSIC, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_COVERS, exist_ok=True)

# 4. РЕЄСТРУЄМО BLUEPRINT (Тільки після створення app!)
app.register_blueprint(tracks_bp)

# --- Допоміжні функції ---
def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Таблиця пісень
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                uploader TEXT DEFAULT 'Anon',
                filename TEXT NOT NULL,
                cover_filename TEXT, 
                is_visible BOOLEAN DEFAULT 1
            )
        ''')

        # Таблиця користувачів
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()



# --- ROUTING (Маршрути) ---

@app.route('/')
def index():
    user = session.get('username')
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs')
        songs = [dict(row) for row in cursor.fetchall()]
    return render_template('index.html', user=user, songs=songs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Заповніть всі поля!', 'error')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                               (username, email, hashed_pw))
                conn.commit()
            flash('Реєстрація успішна! Увійдіть.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Такий користувач або email вже існує!', 'error')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                flash('Невірний email або пароль', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть, щоб завантажувати музику', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        artist = request.form.get('artist')
        uploader = session.get('username') 
        
        if 'audio_file' not in request.files: return redirect(request.url)
        audio = request.files['audio_file']
        
        if audio.filename == '' or not allowed_file(audio.filename, ALLOWED_EXTENSIONS_MUSIC):
            flash('Невірний формат аудіо', 'error')
            return redirect(request.url)

        audio_filename = secure_filename(audio.filename)
        audio.save(os.path.join(UPLOAD_FOLDER_MUSIC, audio_filename))

        cover_filename = None
        if 'cover_file' in request.files:
            cover = request.files['cover_file']
            if cover.filename != '' and allowed_file(cover.filename, ALLOWED_EXTENSIONS_IMAGE):
                safe_cover_name = secure_filename(cover.filename)
                cover.save(os.path.join(UPLOAD_FOLDER_COVERS, safe_cover_name))
                cover_filename = safe_cover_name

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO songs (title, artist, uploader, filename, cover_filename, is_visible) VALUES (?, ?, ?, ?, ?, ?)',
                (title, artist, uploader, audio_filename, cover_filename, 1)
            )
            conn.commit()
        return redirect(url_for('index'))
    return render_template('upload.html')

# Цей роут можна залишити для сумісності зі старим фронтендом,
# але тепер у нас є /api/tracks через blueprint
@app.route('/songs')
def get_songs():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs')
        rows = cursor.fetchall()
        return jsonify([dict(row) for row in rows])

@app.route('/edit/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    if 'user_id' not in session:
        flash('Увійдіть, щоб редагувати', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
        song = cursor.fetchone()

        if not song: return "Song not found", 404
        if song['uploader'] != session.get('username'):
             flash('Ви не можете редагувати чужі треки!', 'error')
             return redirect(url_for('index'))

        if request.method == 'POST':
            new_title = request.form.get('title')
            new_artist = request.form.get('artist')
            is_visible = 1 if request.form.get('is_visible') else 0 
            
            new_cover_filename = song['cover_filename']
            file = request.files.get('cover_file')
            
            if file and file.filename != '' and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMAGE):
                if song['cover_filename']:
                    try:
                        old_path = os.path.join(UPLOAD_FOLDER_COVERS, song['cover_filename'])
                        if os.path.exists(old_path): os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting old cover: {e}")
                
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER_COVERS, filename))
                new_cover_filename = filename

            cursor.execute('''
                UPDATE songs 
                SET title = ?, artist = ?, is_visible = ?, cover_filename = ?
                WHERE id = ?
            ''', (new_title, new_artist, is_visible, new_cover_filename, song_id))
            conn.commit()
            
            flash('Зміни збережено!', 'success')
            return redirect(url_for('index'))
    return render_template('edit.html', song=song)

@app.route('/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT filename, cover_filename FROM songs WHERE id = ?', (song_id,))
        song = cursor.fetchone()
        
        if not song: return jsonify({'success': False, 'message': 'Song not found'}), 404

        try:
            file_path = os.path.join(UPLOAD_FOLDER_MUSIC, song['filename'])
            if os.path.exists(file_path): os.remove(file_path)
            
            if song['cover_filename']:
                cover_path = os.path.join(UPLOAD_FOLDER_COVERS, song['cover_filename'])
                if os.path.exists(cover_path): os.remove(cover_path)
        except Exception as e:
            print(f"Error deleting files: {e}")

        cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        conn.commit()
        return jsonify({'success': True})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=4880)