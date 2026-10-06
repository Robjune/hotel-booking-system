from django.contrib import admin
from django.utils.html import format_html

from .models import Room, RoomImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number',
        'room_type',
        'price_per_night',
        'capacity',
        'is_available',
        'thumbnail',
    )

    list_filter = ('room_type', 'is_available', 'capacity')
    list_editable = ('price_per_night', 'is_available')
    search_fields = ('room_number', 'room_type', 'description')
    readonly_fields = ('thumbnail', 'created_at', 'updated_at')
    inlines = [RoomImageInline]
    actions = ['mark_available', 'mark_unavailable']

    fieldsets = (
        (None, {'fields': ('room_number', 'room_type', 'description', 'amenities')}),
        ('Pricing & capacity', {'fields': ('price_per_night', 'capacity', 'is_available')}),
        ('Main photo', {'fields': ('image', 'thumbnail')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Photo')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:4px;">', obj.image.url
            )
        return '—'

    @admin.action(description='Mark selected rooms as available')
    def mark_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description='Mark selected rooms as unavailable')
    def mark_unavailable(self, request, queryset):
        queryset.update(is_available=False)
