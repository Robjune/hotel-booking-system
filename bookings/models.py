import secrets

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from rooms.models import Room


class BookingQuerySet(models.QuerySet):
    def active(self):
        """Bookings that still block the room (not cancelled)."""
        return self.exclude(status=Booking.Status.CANCELLED)

    def overlapping(self, check_in, check_out):
        # Two stays overlap when each one starts before the other ends.
        # A guest checking out on the same day another checks in is allowed.
        return self.filter(check_in__lt=check_out, check_out__gt=check_in)


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CHECKED_IN = 'checked_in', 'Checked in'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    reference = models.CharField(max_length=12, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings'
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    special_requests = models.TextField(blank=True)
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False,
        help_text='Room price locked in at the time of booking.',
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookingQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} – {self.room} ({self.check_in} to {self.check_out})"

    def get_absolute_url(self):
        return reverse('bookings:detail', args=[self.reference])

    @property
    def nights(self):
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    @property
    def can_cancel(self):
        return (
            self.status in (self.Status.PENDING, self.Status.CONFIRMED)
            and self.check_in > timezone.localdate()
        )

    def clean(self):
        errors = {}
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                errors['check_out'] = 'Check-out must be at least one day after check-in.'
            # Only new bookings have to start in the future; staff may still edit past ones.
            if self._state.adding and self.check_in < timezone.localdate():
                errors['check_in'] = 'Check-in date cannot be in the past.'

        room = self.room if self.room_id else None
        if room:
            if self.guests and self.guests > room.capacity:
                errors['guests'] = (
                    f'This room fits up to {room.capacity} guest{"s" if room.capacity != 1 else ""}.'
                )
            # Reported as a general error: the customer booking form has no "room" field.
            if self._state.adding and not room.is_available:
                errors.setdefault(NON_FIELD_ERRORS, []).append(
                    'This room is not available for booking right now.'
                )

            if self.check_in and self.check_out and 'check_out' not in errors:
                clash = (
                    Booking.objects.active()
                    .filter(room=room)
                    .overlapping(self.check_in, self.check_out)
                    .exclude(pk=self.pk)
                )
                if self.status != self.Status.CANCELLED and clash.exists():
                    errors.setdefault(NON_FIELD_ERRORS, []).append(
                        'Sorry, this room is already reserved for some of those dates. '
                        'Please choose different dates or another room.'
                    )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        if self.price_per_night is None:
            self.price_per_night = self.room.price_per_night
        self.total_price = self.price_per_night * self.nights
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference():
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        while True:
            ref = 'GH-' + ''.join(secrets.choice(alphabet) for _ in range(6))
            if not Booking.objects.filter(reference=ref).exists():
                return ref
