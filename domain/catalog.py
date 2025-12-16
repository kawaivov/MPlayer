import uuid
from dataclasses import dataclass, field
from enum import Enum

class TrackStatus(Enum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    DELETED = "deleted"

@dataclass
class Track:
    # 1. Обов'язкові поля
    title: str
    artist: str
    uploader_id: uuid.UUID
    filename: str
    
    # 2. Поля зі значеннями за замовчуванням
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: TrackStatus = TrackStatus.VISIBLE

    def hide(self):
        self.status = TrackStatus.HIDDEN
    
    def publish(self):
        self.status = TrackStatus.VISIBLE

    def is_available(self) -> bool:
        return self.status == TrackStatus.VISIBLE