SITE_INFO = {
    'name': 'GrandHaven',
    'tagline': 'Hotel & Suites',
    'address': 'Angeles City, Pampanga, Philippines',
    'phone': '+63 912 345 6789',
    'email': 'reservations@grandhaven.example',
}


def site_info(request):
    return {
        'site': SITE_INFO,
        'nav_unread_messages': unread_messages(request),
    }


def unread_messages(request):
    return 0