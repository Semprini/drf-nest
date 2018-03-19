from django.contrib.auth.models import User, Group
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APIClient

from sample_project.app.models import SalesChannel, Sale, TenderType

class SaleAPITests(APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser('superjohn', 'superjohn@snow.com', 'superjohnpassword')
        self.client = APIClient()
        self.client.login(username='superjohn', password='jsuperjohnpassword')
        self.client.force_authenticate(user=self.superuser)
        
        self.channel = SalesChannel.objects.create(name='Store')
        self.tender_type = TenderType.objects.create(name='Cash')
        self.sale = Sale.objects.create( channel=self.channel, store_code="X1", docket_number=1, customer_id="A" )
        
        
    def test_get_sale(self):
        """
        Test that we can GET the sample Sale and check that we get private fields for superuser
        """
        url = '/api/sale/{}/'.format(self.sale.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.exception, False)
        
        
    def test_create_sale(self):
        """
        Ensure we can create a new empty Sale object.
        """
        url = '/api/sale/'
        data = {
            "channel":"http://127.0.0.1:8000/api/sales_channel/Store/",
            "store_code":"X1",
            "docket_number":2,
            "datetime":"2018-02-04T00:40:44.313123Z",
            "total_amount":"0.00",
            "total_amount_excl":"0.00",
            "total_discount":"0.00",
            "total_tax":"0.00",
            "customer_id":"A",
            "tenders":[],
            "sale_items":[]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_create_sale_with_sub_objects(self):
        url = '/api/sale/'
        data = {
            "type": "Sale",
            "channel": "http://127.0.0.1:8000/api/sales_channel/Store/",
            "datetime": "2018-03-19T04:02:23Z",
            "store_code":"X1",
            "docket_number": 1,
            "status": "complete",
            "amount": "1.15",
            "amount_excl": "1.00",
            "discount": "0.00",
            "tax": "0.15",
            "customer_id": None,
            "identification_id": None,
            "pos_id": None,
            "staff_id": None,
            "tenders": [
                {
                    "type": "Tender",
                    "tender_type": "http://127.0.0.1:8000/api/tender_type/Cash/",
                    "amount": "1.15",
                    "reference": None
                }
            ],
            "sale_items": [
                {
                    "type": "SaleItem",
                    "product_offering_id": "1",
                    "supplier_product_id": "1",
                    "product_name": "Test Product",
                    "status": "sold",
                    "status_related_sale": None,
                    "quantity": "1.0000",
                    "unit_of_measure": "each",
                    "amount": "1.15",
                    "amount_excl": "0.15",
                    "discount": "0.00",
                    "tax": "0.15",
                    "retail_price": "0.00"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        