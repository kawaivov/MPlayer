import uuid
from dataclasses import dataclass, field
from typing import List

@dataclass
class Playlist:
    # 1. Обов'язкові поля
    owner_id: uuid.UUID
    name: str
    
    # 2. Поля зі значеннями за замовчуванням
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    track_ids: List[uuid.UUID] = field(default_factory=list)

    def add_track(self, track_id: uuid.UUID):
        if track_id not in self.track_ids:
            self.track_ids.append(track_id)
            print(f"Track {track_id} added to playlist {self.name}")

    def remove_track(self, track_id: uuid.UUID):
        if track_id in self.track_ids:
            self.track_ids.remove(track_id)

    def track_count(self) -> int:
        return len(self.track_ids)