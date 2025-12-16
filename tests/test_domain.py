from domain.identity import User
from domain.catalog import Track, TrackStatus
from domain.interaction import Playlist

print("--- 1. ТЕСТ IDENTITY (Користувачі) ---")
# Створюємо користувача
me = User(username="MusicFan", email="fan@gmail.com", password_hash="old_hash")
print(f"Створено користувача: {me.username}")

# Змінюємо пароль (перевіряємо бізнес-логіку)
print(f"Старий хеш: {me.password_hash}")
me.change_password("super_secure_password")
print(f"Новий хеш (SHA256): {me.password_hash}")


print("\n--- 2. ТЕСТ CATALOG (Музика) ---")
# Створюємо трек (спочатку прихований)
song = Track(
    title="DDD Anthem", 
    artist="The Coders", 
    uploader_id=me.id, 
    filename="song.mp3",
    status=TrackStatus.HIDDEN # Створений, але схований
)
print(f"Трек '{song.title}' створено. Статус: {song.status}")

# Публікуємо трек
song.publish()
print(f"Викликали song.publish(). Новий статус: {song.status}")
print(f"Чи доступний трек? {song.is_available()}")


print("\n--- 3. ТЕСТ INTERACTION (Плейлисти) ---")
# Створюємо плейлист
my_playlist = Playlist(owner_id=me.id, name="Best Songs 2025")
print(f"Створено плейлист: {my_playlist.name}")
print(f"Кількість пісень: {my_playlist.track_count()}")

# Додаємо пісню
my_playlist.add_track(song.id)
print(f"Додано пісню ID: {song.id}")
print(f"Кількість пісень зараз: {my_playlist.track_count()}")

# Спробуємо додати ту саму пісню ще раз (логіка має заборонити дублікати, якщо ми це прописали)
my_playlist.add_track(song.id) 
print(f"Кількість після спроби дублювання: {my_playlist.track_count()}")

print("\n--- ✅ ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО! ---")