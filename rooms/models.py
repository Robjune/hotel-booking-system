from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class RoomQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)


class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    description = models.TextField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    capacity = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of guests.',
    )
    is_available = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this room from booking (e.g. under maintenance).',
    )
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    amenities = models.CharField(
        max_length=255,
        blank=True,
        help_text='Comma-separated, e.g. "Free Wi-Fi, Air conditioning, Smart TV".',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RoomQuerySet.as_manager()

    class Meta:
        ordering = ['room_number']

    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()}"

    def get_absolute_url(self):
        return reverse('rooms:room_detail', args=[self.pk])

    @property
    def amenity_list(self):
        return [item.strip() for item in self.amenities.split(',') if item.strip()]


class RoomImage(models.Model):
    """Extra gallery photos shown on the room detail page."""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/gallery/')
    caption = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Photo for {self.room}"
