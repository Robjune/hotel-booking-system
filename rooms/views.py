from django.shortcuts import get_object_or_404, render
from django.utils.http import urlencode

from .models import Room
from .search import search_rooms


def room_list(request):
    rooms, search_context = search_rooms(request, Room.objects.all())

    selected_type = request.GET.get('type', '')
    valid_types = dict(Room.ROOM_TYPES)
    if selected_type not in valid_types:
        selected_type = ''

    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'selected_type': selected_type,
        'selected_type_label': valid_types.get(selected_type, 'All Rooms'),
        **search_context,
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    similar_rooms = (
        Room.objects.available()
        .filter(room_type=room.room_type)
        .exclude(pk=room.pk)[:3]
    )
    context = {
        'room': room,
        'gallery': room.images.all(),
        'similar_rooms': similar_rooms,
        # Keep dates/guests chosen in the search so the booking form is pre-filled.
        'booking_params': urlencode({
            key: request.GET[key] for key in ('check_in', 'check_out', 'guests') if request.GET.get(key)
        }),
    }
    return render(request, 'rooms/room_detail.html', context)
