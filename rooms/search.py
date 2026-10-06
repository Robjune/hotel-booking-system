from django.db.models import Q


def search_rooms(request, queryset):
    rooms = queryset

    query = request.GET.get('q', '').strip()
    room_type = request.GET.get('room_type', '').strip()
    capacity = request.GET.get('capacity', '').strip()
    guests = request.GET.get('guests', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if query:
        rooms = rooms.filter(
            Q(room_number__icontains=query) |
            Q(room_type__icontains=query) |
            Q(description__icontains=query)
        )

    if room_type:
        rooms = rooms.filter(room_type=room_type)

    if capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(capacity))
        except ValueError:
            pass

    if guests:
        try:
            rooms = rooms.filter(capacity__gte=int(guests))
        except ValueError:
            pass

    if min_price:
        try:
            rooms = rooms.filter(price_per_night__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            rooms = rooms.filter(price_per_night__lte=float(max_price))
        except ValueError:
            pass

    search_context = {
        'query': query,
        'selected_room_type': room_type,
        'selected_capacity': capacity,
        'selected_guests': guests,
        'min_price': min_price,
        'max_price': max_price,
    }

    return rooms, search_context