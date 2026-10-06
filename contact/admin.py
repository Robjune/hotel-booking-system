from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'phone', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')
    actions = ['mark_read', 'mark_unread']

    def has_add_permission(self, request):
        # Messages come from the public contact form only.
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Opening a message marks it as read.
        ContactMessage.objects.filter(pk=object_id).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description='Mark selected messages as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected messages as unread')
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)
