from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room


class HomeTests(TestCase):
    def test_home_shows_featured_rooms(self):
        Room.objects.create(room_number='301', room_type='suite', description='Suite',
                            price_per_night=Decimal('8900'), capacity=4)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Room 301')

    def test_unknown_page_is_404(self):
        self.assertEqual(self.client.get('/no-such-page/').status_code, 404)


class DashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'x', is_staff=True)
        self.guest = User.objects.create_user('guest', 'guest@example.com', 'x')
        room = Room.objects.create(room_number='101', room_type='standard', description='Std',
                                   price_per_night=Decimal('2500'), capacity=2)
        today = timezone.localdate()
        self.booking = Booking.objects.create(user=self.guest, room=room,
                                              check_in=today + timedelta(days=1),
                                              check_out=today + timedelta(days=3))

    def test_dashboard_is_staff_only(self):
        self.client.force_login(self.guest)
        self.assertEqual(self.client.get(reverse('core:dashboard')).status_code, 302)
        self.client.force_login(self.staff)
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.reference)

    def test_staff_can_confirm_booking(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('core:update_booking_status', args=[self.booking.reference]),
                         {'status': 'confirmed'})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)

    def test_guest_cannot_change_status(self):
        self.client.force_login(self.guest)
        self.client.post(reverse('core:update_booking_status', args=[self.booking.reference]),
                         {'status': 'confirmed'})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.PENDING)
