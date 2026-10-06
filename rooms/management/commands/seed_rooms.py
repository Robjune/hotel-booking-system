from decimal import Decimal

from django.core.management.base import BaseCommand

from rooms.models import Room

SAMPLE_ROOMS = [
    {
        'room_number': '101',
        'room_type': 'standard',
        'price_per_night': Decimal('2500.00'),
        'capacity': 2,
        'description': 'A cozy, well-appointed room with a queen-size bed, '
                       'work desk and city views. Perfect for solo travellers and couples.',
        'amenities': 'Free Wi-Fi, Air conditioning, Smart TV, Hot shower, Work desk',
    },
    {
        'room_number': '102',
        'room_type': 'standard',
        'price_per_night': Decimal('2300.00'),
        'capacity': 2,
        'description': 'A bright twin room with two single beds, ideal for friends '
                       'or colleagues travelling together.',
        'amenities': 'Free Wi-Fi, Air conditioning, Smart TV, Hot shower',
    },
    {
        'room_number': '201',
        'room_type': 'deluxe',
        'price_per_night': Decimal('4200.00'),
        'capacity': 3,
        'description': 'Spacious deluxe room with a king-size bed, sofa lounge area '
                       'and a large window overlooking the garden.',
        'amenities': 'Free Wi-Fi, Air conditioning, Smart TV, Mini bar, Coffee maker, Bathtub',
    },
    {
        'room_number': '202',
        'room_type': 'deluxe',
        'price_per_night': Decimal('4500.00'),
        'capacity': 2,
        'description': 'Deluxe room with a private balcony, premium bedding and '
                       'a rain shower bathroom.',
        'amenities': 'Free Wi-Fi, Air conditioning, Balcony, Mini bar, Rain shower, Bathrobes',
        'is_available': False,
    },
    {
        'room_number': '301',
        'room_type': 'suite',
        'price_per_night': Decimal('8900.00'),
        'capacity': 4,
        'description': 'Our signature suite with a separate living room, dining area, '
                       'panoramic city views and complimentary breakfast for two.',
        'amenities': 'Free Wi-Fi, Air conditioning, Living room, Dining area, Bathtub, '
                     'Free breakfast, Mini bar, Nespresso machine',
    },
    {
        'room_number': '401',
        'room_type': 'family',
        'price_per_night': Decimal('5800.00'),
        'capacity': 6,
        'description': 'Generous family room with one king bed and two bunk beds, '
                       'a play corner for kids and plenty of storage.',
        'amenities': 'Free Wi-Fi, Air conditioning, Smart TV, Kids corner, Refrigerator, Extra towels',
    },
]


class Command(BaseCommand):
    help = 'Create sample rooms for demos and local testing (safe to run more than once).'

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_ROOMS:
            defaults = {k: v for k, v in data.items() if k != 'room_number'}
            _, created = Room.objects.get_or_create(
                room_number=data['room_number'], defaults=defaults
            )
            created_count += created

        self.stdout.write(self.style.SUCCESS(
            f'{created_count} sample room(s) created, '
            f'{len(SAMPLE_ROOMS) - created_count} already existed.'
        ))
