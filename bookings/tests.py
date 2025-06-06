from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import FitnessClass, Booking
from django.utils import timezone
import pytz

class BookingAPITestCase(TestCase):
    def setUp(self):
        self.class_url = reverse('fitnessclass-list')
        self.book_url = reverse('book_class')
        self.bookings_url = reverse('get_bookings')
        ist = pytz.timezone("Asia/Kolkata")
        dt = timezone.now().astimezone(ist) + timezone.timedelta(days=1)

        self.fitness_class = FitnessClass.objects.create(
            name="Test Class",
            datetime=dt,
            instructor="John Doe",
            available_slots=2
        )

    def test_create_fitness_class(self):
        data = {
            "name": "HIIT",
            "datetime": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
            "instructor": "John Doe",
            "available_slots": 10
        }
        response = self.client.post(self.class_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_book_fitness_class_successfully(self):
        data = {
            "class_id": self.fitness_class.id,
            "client_name": "Test User",
            "client_email": "user@example.com"
        }
        response = self.client.post(self.book_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_overbooking_not_allowed(self):
        self.fitness_class.available_slots = 0
        self.fitness_class.save()
        data = {
            "class_id": self.fitness_class.id,
            "client_name": "User",
            "client_email": "user@example.com"
        }
        response = self.client.post(self.book_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No available slots", response.data['error'])

    def test_duplicate_booking_not_allowed(self):
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="User",
            client_email="user@example.com"
        )
        self.fitness_class.available_slots = 5
        self.fitness_class.save()
        data = {
            "class_id": self.fitness_class.id,
            "client_name": "User",
            "client_email": "user@example.com"
        }
        response = self.client.post(self.book_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already booked", response.data['error'])

    def test_get_bookings_by_email(self):
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="User",
            client_email="user@example.com"
        )
        response = self.client.get(self.bookings_url, {"email": "user@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
