from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rooms.models import Room

from .models import Booking


def days(n):
    return timezone.localdate() + timedelta(days=n)


class BookingTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('guest', 'guest@example.com', 'pass12345!')
        self.other = User.objects.create_user('other', 'other@example.com', 'pass12345!')
        self.room = Room.objects.create(
            room_number='201', room_type='deluxe', description='Deluxe',
            price_per_night=Decimal('4000.00'), capacity=2,
        )

    def make_booking(self, check_in, check_out, user=None, **extra):
        booking = Booking(
            user=user or self.user, room=self.room,
            check_in=check_in, check_out=check_out, guests=extra.pop('guests', 2), **extra,
        )
        booking.full_clean()
        booking.save()
        return booking


class BookingModelTests(BookingTestBase):
    def test_nights_and_total_calculated(self):
        booking = self.make_booking(days(1), days(4))
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.total_price, Decimal('12000.00'))
        self.assertTrue(booking.reference.startswith('GH-'))

    def test_price_locked_when_room_price_changes(self):
        booking = self.make_booking(days(1), days(3))
        self.room.price_per_night = Decimal('9999.00')
        self.room.save()
        booking.refresh_from_db()
        booking.save()
        self.assertEqual(booking.total_price, Decimal('8000.00'))

    def test_checkout_must_be_after_checkin(self):
        with self.assertRaises(ValidationError) as ctx:
            self.make_booking(days(3), days(3))
        self.assertIn('check_out', ctx.exception.message_dict)

    def test_checkin_cannot_be_in_past(self):
        with self.assertRaises(ValidationError) as ctx:
            self.make_booking(days(-1), days(2))
        self.assertIn('check_in', ctx.exception.message_dict)

    def test_guests_cannot_exceed_capacity(self):
        with self.assertRaises(ValidationError) as ctx:
            self.make_booking(days(1), days(2), guests=3)
        self.assertIn('guests', ctx.exception.message_dict)

    def test_unavailable_room_cannot_be_booked(self):
        self.room.is_available = False
        self.room.save()
        with self.assertRaises(ValidationError):
            self.make_booking(days(1), days(2))

    def test_overlapping_booking_rejected(self):
        self.make_booking(days(5), days(8))
        for check_in, check_out in [(days(4), days(6)), (days(6), days(7)), (days(7), days(10)), (days(4), days(10))]:
            with self.assertRaises(ValidationError, msg=f'{check_in}–{check_out} should clash'):
                self.make_booking(check_in, check_out, user=self.other)

    def test_back_to_back_bookings_allowed(self):
        self.make_booking(days(5), days(8))
        self.make_booking(days(8), days(10), user=self.other)
        self.make_booking(days(2), days(5), user=self.other)
        self.assertEqual(Booking.objects.count(), 3)

    def test_cancelled_booking_frees_dates(self):
        first = self.make_booking(days(5), days(8))
        first.status = Booking.Status.CANCELLED
        first.save()
        self.make_booking(days(5), days(8), user=self.other)

    def test_restoring_cancelled_booking_onto_taken_dates_fails(self):
        first = self.make_booking(days(5), days(8))
        first.status = Booking.Status.CANCELLED
        first.save()
        self.make_booking(days(6), days(7), user=self.other)
        first.status = Booking.Status.CONFIRMED
        with self.assertRaises(ValidationError):
            first.full_clean()


class BookingViewTests(BookingTestBase):
    def test_booking_requires_login(self):
        url = reverse('bookings:create', args=[self.room.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_create_booking_flow(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('bookings:create', args=[self.room.pk]), {
            'check_in': days(1), 'check_out': days(3), 'guests': 2,
        }, follow=True)
        booking = Booking.objects.get()
        self.assertRedirects(response, booking.get_absolute_url())
        self.assertContains(response, booking.reference)
        self.assertContains(response, '8,000.00')
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.Status.PENDING)

    def test_overlap_shows_error_on_form(self):
        self.make_booking(days(2), days(5), user=self.other)
        self.client.force_login(self.user)
        response = self.client.post(reverse('bookings:create', args=[self.room.pk]), {
            'check_in': days(3), 'check_out': days(4), 'guests': 1,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already reserved')
        self.assertEqual(Booking.objects.count(), 1)

    def test_form_prefilled_from_query(self):
        self.client.force_login(self.user)
        url = reverse('bookings:create', args=[self.room.pk])
        response = self.client.get(url, {'check_in': days(1).isoformat(), 'guests': 2})
        self.assertContains(response, f'value="{days(1).isoformat()}"')

    def test_other_users_cannot_see_booking(self):
        booking = self.make_booking(days(1), days(2))
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(booking.get_absolute_url()).status_code, 404)

    def test_my_bookings_lists_only_own(self):
        mine = self.make_booking(days(1), days(2))
        theirs = self.make_booking(days(3), days(4), user=self.other)
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookings:my_bookings'))
        self.assertContains(response, mine.reference)
        self.assertNotContains(response, theirs.reference)

    def test_cancel_booking(self):
        booking = self.make_booking(days(3), days(5))
        self.client.force_login(self.user)
        self.client.post(reverse('bookings:cancel', args=[booking.reference]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)
