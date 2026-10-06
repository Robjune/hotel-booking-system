from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'user', 'room', 'check_in', 'check_out',
        'nights', 'guests', 'total_price', 'status', 'created_at',
    )
    list_filter = ('status', 'room__room_type', 'check_in')
    list_editable = ('status',)
    search_fields = ('reference', 'user__username', 'user__email', 'room__room_number')
    date_hierarchy = 'check_in'
    autocomplete_fields = ('user', 'room')
    readonly_fields = ('reference', 'price_per_night', 'total_price', 'created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed']

    fieldsets = (
        (None, {'fields': ('reference', 'user', 'room', 'status')}),
        ('Stay', {'fields': ('check_in', 'check_out', 'guests', 'special_requests')}),
        ('Price', {'fields': ('price_per_night', 'total_price')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Nights')
    def nights(self, obj):
        return obj.nights

    def _set_status(self, request, queryset, status):
        updated, failed = 0, []
        for booking in queryset:
            booking.status = status
            try:
                booking.full_clean()  # blocks restoring a cancelled booking onto taken dates
            except ValidationError:
                failed.append(booking.reference)
                continue
            booking.save(update_fields=['status', 'updated_at'])
            updated += 1
        if updated:
            self.message_user(request, f'{updated} booking(s) updated.', messages.SUCCESS)
        if failed:
            self.message_user(
                request, f'Not updated (dates clash with another booking): {", ".join(failed)}',
                messages.ERROR,
            )

    @admin.action(description='Mark selected bookings as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._set_status(request, queryset, Booking.Status.CONFIRMED)

    @admin.action(description='Mark selected bookings as Cancelled')
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Booking.Status.CANCELLED)

    @admin.action(description='Mark selected bookings as Completed')
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, Booking.Status.COMPLETED)
