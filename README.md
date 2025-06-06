# 🏋️‍♀️ Fitness Booking API

This Django REST API allows users to:
- View upcoming fitness classes
- Create new classes (admin)
- Book a spot in a class
- Retrieve bookings by email

---

## 📦 Setup Instructions

### 1. Clone the repository

git clone [https://github.com/your-username/fitness-booking-api.git](https://github.com/Praveenkumar9392/Fictional-Fitness-Studio.git)

cd fitness-booking-api

python -m venv myenv

source myenv/bin/activate   # On Windows: myenv\Scripts\activate

pip install -r requirements.txt

python manage.py runserver

python manage.py migrate


 API Endpoints
1. List upcoming fitness classes
GET /api/classes/?tz=Asia/Kolkata

Response:

[
  {
    "id": 1,
    "name": "Yoga",
    "datetime": "2025-06-10T09:00:00+05:30",
    "instructor": "Alice",
    "available_slots": 5
  }
]
2. Create a fitness class (Admin)
POST /api/classes/

Sample Request:

{
  "name": "Zumba",
  "datetime": "2025-06-15T18:00:00",
  "instructor": "Bob",
  "available_slots": 10
}
Response:

201 Created with class data

400 Bad Request on errors

3. Book a class
POST /book/

Sample Request:

{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}
Response:

{
  "id": 5,
  "fitness_class": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "booked_at": "2025-06-05T14:30:00Z"
}
Error Examples:

400: Already booked

404: Class not found

4. View bookings by email
GET /bookings/?email=john@example.com

Response:

[
  {
    "fitness_class": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "booked_at": "2025-06-05T14:30:00Z"
  }
]

 Testing
To run the test suite:

python manage.py test
🛠 Technologies Used
Python 3.x

Django

Django REST Framework

SQLite (default DB)

Postman (for testing)

 Sample Postman Input
Booking Request

{
  "class_id": 1,
  "client_name": "Test User",
  "client_email": "test@example.com"
}
Create Class

{
  "name": "Pilates",
  "datetime": "2025-06-20T07:00:00",
  "instructor": "Clara",
  "available_slots": 8
}







