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
        'nav_unread_messages': _unread_messages(request),
    }


def _unread_messages(request):
    user = getattr(request, 'user', None)
    if not (user and user.is_staff):
        return 0
    from contact.models import ContactMessage
    return ContactMessage.objects.filter(is_read=False).count()
