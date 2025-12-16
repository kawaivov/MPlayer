# 3. Стиль API та обробка помилок

**Дата:** 2025-10-XX  
**Статус:** Прийнято

## Рішення
* Використовуємо RESTful API.
* Формат обміну: JSON.
* Контракт фіксується в OpenAPI (Swagger).

## Формат помилки
У разі помилки сервер повертає JSON:
```json
{
  "error": "ErrorType",
  "message": "Human readable message",
  "details": [] 
}