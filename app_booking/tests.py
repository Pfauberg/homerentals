from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from app_accounts.models import CustomUser
from app_property.models import Property
from .models import Booking
import datetime as dt


class BookingFlowTests(APITestCase):
    def setUp(self):
        self.tenant   = CustomUser.objects.create_user('alice', 'pass', role='user')
        self.landlord = CustomUser.objects.create_user('bob',   'pass', role='landlord')
        self.prop = Property.objects.create(
            owner=self.landlord, title='Nice flat', type='apartment',
            description='...', price_per_day=100, city='Berlin', address='Main 1',
            beds=2, available_from=dt.date.today() + dt.timedelta(days=1),
            available_to=dt.date.today() + dt.timedelta(days=10),
            status='active'
        )

    def test_booking_lifecycle(self):
        self.client.login(username='alice', password='pass')
        url = reverse('api_booking_create')
        resp = self.client.post(url, data={
            'property': self.prop.id,
            'start_date': str(self.prop.available_from),
            'end_date':   str(self.prop.available_from + dt.timedelta(days=2)),
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        booking_id = resp.data['id']

        self.client.logout()
        self.client.login(username='bob', password='pass')
        detail = reverse('api_booking_detail', args=[booking_id])
        resp = self.client.patch(detail, data={'status': 'confirmed'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'confirmed')

        self.prop.refresh_from_db()
        self.assertEqual(
            self.prop.available_to,
            (dt.date.fromisoformat(resp.data['start_date']) - dt.timedelta(days=1))
        )
