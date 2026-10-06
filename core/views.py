from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from bookings.models import Booking
from contact.models import ContactMessage
from rooms.models import Room


def home(request):
    today = timezone.localdate()
    featured = Room.objects.available().order_by('-price_per_night')[:3]
    room_types = (
        Room.objects.available()
        .values('room_type')
        .annotate(count=Count('id'))
        .order_by('room_type')
    )
    type_labels = dict(Room.ROOM_TYPES)
    return render(request, 'core/home.html', {
        'featured_rooms': featured,
        'room_types': [
            {'value': row['room_type'], 'label': type_labels.get(row['room_type'], row['room_type']),
             'count': row['count']}
            for row in room_types
        ],
        'room_type_choices': Room.ROOM_TYPES,
        'default_check_in': today + timedelta(days=1),
        'default_check_out': today + timedelta(days=2),
    })


@staff_member_required
def dashboard(request):
    today = timezone.localdate()
    bookings = Booking.objects.select_related('room', 'user')
    active = bookings.active()

    occupied_today = active.filter(check_in__lte=today, check_out__gt=today).count()
    total_rooms = Room.objects.count()

    context = {
        'stats': {
            'rooms': total_rooms,
            'available_rooms': Room.objects.available().count(),
            'occupied_today': occupied_today,
            'occupancy_pct': round(occupied_today * 100 / total_rooms) if total_rooms else 0,
            'pending': bookings.filter(status=Booking.Status.PENDING).count(),
            'upcoming': active.filter(check_in__gte=today).count(),
            'customers': User.objects.filter(is_staff=False).count(),
            'revenue': active.exclude(status=Booking.Status.PENDING)
                             .aggregate(total=Sum('total_price'))['total'] or 0,
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        },
        'pending_bookings': bookings.filter(status=Booking.Status.PENDING).order_by('check_in')[:8],
        'arrivals': active.filter(check_in=today),
        'departures': active.filter(check_out=today),
        'recent_bookings': bookings[:8],
        'recent_messages': ContactMessage.objects.all()[:5],
        'recent_customers': User.objects.filter(is_staff=False)
                                .annotate(num_bookings=Count('bookings'))
                                .order_by('-date_joined')[:5],
        'status_choices': Booking.Status.choices,
    }
    return render(request, 'core/dashboard.html', context)


@staff_member_required
@require_POST
def update_booking_status(request, reference):
    booking = get_object_or_404(Booking, reference=reference)
    new_status = request.POST.get('status')
    if new_status not in Booking.Status.values:
        messages.error(request, 'Invalid booking status.')
        return redirect('core:dashboard')

    booking.status = new_status
    try:
        booking.full_clean()  # re-checks for clashes, e.g. when restoring a cancelled booking
    except ValidationError as exc:
        messages.error(request, f'{booking.reference}: ' + ' '.join(exc.messages))
    else:
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Booking {booking.reference} marked as {booking.get_status_display()}.')
    return redirect('core:dashboard')
