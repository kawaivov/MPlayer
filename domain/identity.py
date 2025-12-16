import uuid
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class User:
    # 1. Спочатку обов'язкові поля (без значень за замовчуванням)
    username: str
    email: str
    password_hash: str
    
    # 2. Потім поля з дефолтними значеннями (id створюється саме)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    registered_at: datetime = field(default_factory=datetime.now)

    def change_password(self, new_password: str):
        self.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        print(f"Password changed for user {self.username}")

    def __eq__(self, other):
        return self.id == other.id