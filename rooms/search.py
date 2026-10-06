from django.shortcuts import render
from django.db.models import Q

from .models import Room


def search_rooms(request):
    rooms = Room.objects.all()

    query = request.GET.get('q', '').strip()
    room_type = request.GET.get('room_type', '').strip()
    capacity = request.GET.get('capacity', '').strip()

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

    return render(
        request,
        'rooms/room_list.html',
        {
            'rooms': rooms,
            'query': query,
        }
    )