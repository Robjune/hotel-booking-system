from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Thank you for reaching out! Our team will get back to you within 24 hours.',
            )
            return redirect('contact:contact')
        messages.error(request, 'Please fix the errors below.')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'name': request.user.get_full_name(), 'email': request.user.email}
        form = ContactForm(initial=initial)
    return render(request, 'contact/contact.html', {'form': form})
