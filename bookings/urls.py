# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FitnessClassViewSet, book_class, get_bookings

router = DefaultRouter()
router.register(r'classes', FitnessClassViewSet, basename='fitnessclass')

urlpatterns = [
    path('', include(router.urls)),

]
