from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactTests(TestCase):
    def test_page_loads(self):
        self.assertEqual(self.client.get(reverse('contact:contact')).status_code, 200)

    def test_valid_message_saved_with_success_message(self):
        response = self.client.post(reverse('contact:contact'), {
            'name': 'Juan', 'email': 'juan@example.com', 'subject': 'Group booking',
            'message': 'Do you offer discounts for 10 rooms?',
        }, follow=True)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertContains(response, 'Thank you for reaching out')

    def test_invalid_message_rejected(self):
        response = self.client.post(reverse('contact:contact'), {
            'name': '', 'email': 'not-an-email', 'subject': 'Hi', 'message': 'short',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, 'at least 10 characters')
