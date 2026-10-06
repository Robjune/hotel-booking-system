from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'phone', 'subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }
        labels = {'phone': 'Phone (optional)'}

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Please write at least 10 characters.')
        return message
