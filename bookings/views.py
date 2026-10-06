from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from rooms.models import Room

from .forms import BookingForm
from .models import Booking


@login_required
def create_booking(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if not room.is_available:
        messages.error(request, f'Room {room.room_number} is not available for booking right now.')
        return redirect(room)

    if request.method == 'POST':
        form = BookingForm(request.POST, room=room, user=request.user)
        if form.is_valid():
            booking = form.save()
            messages.success(
                request,
                f'Your reservation {booking.reference} has been received! '
                'We will confirm it shortly.',
            )
            return redirect(booking)
        messages.error(request, 'Please fix the errors below.')
    else:
        # Pre-fill dates/guests when coming from the search form.
        initial = {key: request.GET[key] for key in ('check_in', 'check_out', 'guests') if request.GET.get(key)}
        form = BookingForm(initial=initial, room=room, user=request.user)

    upcoming = (
        Booking.objects.active()
        .filter(room=room, check_out__gt=timezone.localdate())
        .order_by('check_in')
        .values('check_in', 'check_out')[:6]
    )
    return render(request, 'bookings/booking_form.html', {
        'room': room,
        'form': form,
        'booked_ranges': upcoming,
    })


def _get_own_booking(request, reference):
    booking = get_object_or_404(Booking.objects.select_related('room', 'user'), reference=reference)
    if booking.user != request.user and not request.user.is_staff:
        raise Http404
    return booking


@login_required
def booking_detail(request, reference):
    booking = _get_own_booking(request, reference)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def my_bookings(request):
    today = timezone.localdate()
    bookings = request.user.bookings.select_related('room')
    return render(request, 'bookings/my_bookings.html', {
        'upcoming': bookings.active().filter(check_out__gte=today).order_by('check_in'),
        'past': bookings.filter(Q(check_out__lt=today) | Q(status=Booking.Status.CANCELLED)),
    })


@login_required
@require_POST
def cancel_booking(request, reference):
    booking = _get_own_booking(request, reference)
    if booking.can_cancel:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Booking {booking.reference} has been cancelled.')
    else:
        messages.error(request, 'This booking can no longer be cancelled.')
    return redirect(booking)
