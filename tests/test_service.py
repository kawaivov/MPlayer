import unittest
import uuid  # <-- Додали імпорт
from service.track_service import TrackService

class TestTrackService(unittest.TestCase):
    
    def setUp(self):
        self.service = TrackService()

    def test_create_track_success(self):
        """Тест: успішне створення треку"""
        
        # Генеруємо справжній UUID для тесту, щоб сервіс не сварився
        valid_user_id = str(uuid.uuid4()) 

        result = self.service.create_track(
            title="Test Song",
            artist="Test Artist",
            uploader_id=valid_user_id # <-- Передаємо валідний ID
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Song")
        print("Test Create: OK")

    def test_get_track_missing(self):
        """Тест: запит неіснуючого треку повертає None"""
        result = self.service.get_track_by_id(999999) 
        self.assertIsNone(result)
        print("Test Missing: OK")

if __name__ == '__main__':
    unittest.main()