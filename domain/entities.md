# Сутності та їх атрибути

## 1. Context: Identity
### User (Aggregate Root)
* `id`: UUID
* `username`: String
* `email`: String
* `password_hash`: String
* `registered_at`: DateTime
* **Methods:** `change_password()`, `update_profile()`

## 2. Context: Catalog
### Track (Aggregate Root)
* `id`: UUID
* `title`: String
* `artist_name`: String
* `file_path`: String
* `cover_path`: String
* `duration_seconds`: Integer
* `status`: Enum(VISIBLE, HIDDEN)
* **Methods:** `publish()`, `hide()`, `update_metadata()`

## 3. Context: Interaction
### Playlist (Aggregate Root)
* `id`: UUID
* `owner_id`: UUID (Reference to User)
* `name`: String
* `is_public`: Boolean
* `tracks`: List[TrackID]
* **Methods:** `add_track()`, `remove_track()`, `rename()`