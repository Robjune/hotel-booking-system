from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'guests': forms.NumberInput(attrs={'min': 1}),
            'special_requests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Early check-in, extra pillows, dietary needs… (optional)',
            }),
        }
        labels = {
            'check_in': 'Check-in',
            'check_out': 'Check-out',
            'guests': 'Guests',
        }

    def __init__(self, *args, room, user, **kwargs):
        super().__init__(*args, **kwargs)
        # Model.clean() needs these before validation runs.
        self.instance.room = room
        self.instance.user = user
        today = timezone.localdate().isoformat()
        self.fields['check_in'].widget.attrs['min'] = today
        self.fields['check_out'].widget.attrs['min'] = today
        self.fields['guests'].widget.attrs['max'] = room.capacity
