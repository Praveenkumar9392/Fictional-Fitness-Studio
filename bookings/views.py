# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timezone import localtime
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer, BookingRequestSerializer
import pytz
import logging
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

logger = logging.getLogger(__name__)

def validate_required_fields(data, required_fields):
    """Check if all required fields are present in the data."""
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing field(s): {', '.join(missing)}"
    return True, None

def parse_and_localize_datetime(datetime_str, timezone_str="Asia/Kolkata"):
    """Parse ISO datetime string and localize or convert to specified timezone."""
    dt = parse_datetime(datetime_str)
    if dt is None:
        raise ValueError("Invalid datetime format.")

    tz = pytz.timezone(timezone_str)
    if dt.tzinfo is None:
        # Naive datetime, localize it
        return tz.localize(dt)
    else:
        # Aware datetime, convert to target timezone
        return dt.astimezone(tz)

class FitnessClassViewSet(viewsets.ModelViewSet):
    queryset = FitnessClass.objects.all()
    serializer_class = FitnessClassSerializer
    permission_classes = [AllowAny]


    def list(self, request, *args, **kwargs):
        tz = request.GET.get("tz", "Asia/Kolkata")
        try:
            timezone.activate(pytz.timezone(tz))
        except Exception:
            timezone.activate(pytz.timezone("Asia/Kolkata"))

        now = timezone.now()
        upcoming_classes = FitnessClass.objects.filter(datetime__gte=now)
        for fc in upcoming_classes:
            fc.datetime = localtime(fc.datetime)
        serializer = self.get_serializer(upcoming_classes, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        required_fields = ["name", "datetime", "instructor", "available_slots"]

        # Validate required fields
        valid, error_msg = validate_required_fields(data, required_fields)
        if not valid:
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate and convert available_slots
            available_slots = int(data['available_slots'])
            if available_slots < 1:
                return Response(
                    {"error": "Available slots must be at least 1."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parse and localize datetime
            dt = parse_and_localize_datetime(data['datetime'])

            # Create FitnessClass instance
            fitness_class = FitnessClass.objects.create(
                name=data['name'],
                datetime=dt,
                instructor=data['instructor'],
                available_slots=available_slots
            )
            logger.info(f"Created class: {fitness_class}")

            return Response(
                FitnessClassSerializer(fitness_class).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as ve:
            logger.error(f"Validation error creating class: {ve}")
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating class: {e}")
            return Response(
                {"error": "Failed to create class due to server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def book_class(request):
    serializer = BookingRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            class_id = serializer.validated_data['class_id']
            client_name = serializer.validated_data['client_name']
            client_email = serializer.validated_data['client_email']

            fitness_class = FitnessClass.objects.get(id=class_id)
            if fitness_class.available_slots <= 0:
                return Response({"error": "No available slots."}, status=status.HTTP_400_BAD_REQUEST)

            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=client_email
            ).exists()

            if existing_booking:
                return Response({"error": "You have already booked this class."}, status=status.HTTP_400_BAD_REQUEST)

            booking = Booking.objects.create(
                fitness_class=fitness_class,
                client_name=client_name,
                client_email=client_email
            )
            fitness_class.available_slots -= 1
            fitness_class.save()
            logger.info(f"Booking successful: {booking}")
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        except FitnessClass.DoesNotExist:
            return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Booking failed: {str(e)}")
            return Response({"error": "Booking failed due to a server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_bookings(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_email(email)
        bookings = Booking.objects.filter(client_email=email)
        return Response(BookingSerializer(bookings, many=True).data)
    except ValidationError:
        return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

