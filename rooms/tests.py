from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Room


class RoomModelTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            room_number='101',
            room_type='deluxe',
            description='Nice room',
            price_per_night=Decimal('3000.00'),
            capacity=2,
            amenities='Wi-Fi, TV , ,Mini bar',
        )

    def test_str(self):
        self.assertEqual(str(self.room), 'Room 101 - Deluxe Room')

    def test_amenity_list_strips_blanks(self):
        self.assertEqual(self.room.amenity_list, ['Wi-Fi', 'TV', 'Mini bar'])

    def test_available_queryset(self):
        Room.objects.create(
            room_number='102', room_type='standard', description='x',
            price_per_night=Decimal('1000'), is_available=False,
        )
        self.assertEqual(list(Room.objects.available()), [self.room])

    def test_invalid_price_and_capacity_rejected(self):
        room = Room(room_number='999', room_type='suite', description='x',
                    price_per_night=Decimal('0'), capacity=0)
        with self.assertRaises(ValidationError) as ctx:
            room.full_clean()
        self.assertIn('price_per_night', ctx.exception.message_dict)
        self.assertIn('capacity', ctx.exception.message_dict)


class RoomViewTests(TestCase):
    def setUp(self):
        self.standard = Room.objects.create(
            room_number='101', room_type='standard', description='Standard room',
            price_per_night=Decimal('2500'), capacity=2,
        )
        self.suite = Room.objects.create(
            room_number='301', room_type='suite', description='Suite room',
            price_per_night=Decimal('8900'), capacity=4,
        )

    def test_list_shows_all_rooms(self):
        response = self.client.get(reverse('rooms:room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Room 101')
        self.assertContains(response, 'Room 301')

    def test_list_filters_by_type(self):
        response = self.client.get(reverse('rooms:room_list'), {'type': 'suite'})
        self.assertContains(response, 'Room 301')
        self.assertNotContains(response, 'Room 101')

    def test_list_ignores_unknown_type(self):
        response = self.client.get(reverse('rooms:room_list'), {'type': 'bogus'})
        self.assertContains(response, '2 rooms found')

    def test_detail(self):
        response = self.client.get(self.suite.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '8,900.00')
        self.assertContains(response, 'Suite')

    def test_detail_404(self):
        response = self.client.get(reverse('rooms:room_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)
