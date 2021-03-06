from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from sample_project.app.models import SalesChannel, Sale, TenderType, Store


class SaleAPITests(APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser('superjohn', 'superjohn@snow.com', 'superjohnpassword')
        self.client = APIClient()
        self.client.login(username='superjohn', password='jsuperjohnpassword')
        self.client.force_authenticate(user=self.superuser)

        self.channel = SalesChannel.objects.create(name='InStore')
        self.store = Store.objects.create(code="FOO1", name='Foo Store')
        self.tender_type = TenderType.objects.create(name='Cash')
        self.sale = Sale.objects.create(store=self.store, docket_number=1, customer_id="A")
        self.sale.channel.add(self.channel)

    def test_get_sale(self):
        """
        Test that we can GET the sample Sale and check that we get private fields for superuser
        """
        url = '/api/sale/{}/'.format(self.sale.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.exception, False)

    def test_create_sale(self):
        """
        Ensure we can create a new empty Sale object using URL representation of the store.
        """
        url = '/api/sale/'
        data = {
            "channel": [
                "http://127.0.0.1:8000/api/sales_channel/InStore/"
            ],
            "store": "http://127.0.0.1:8000/api/store/FOO1/",
            "docket_number": 2,
            "datetime": "2018-02-04T00:40:44.313123Z",
            "total_amount": "0.00",
            "tenders": [],
            "sale_items": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_sale(self):
        """
        Ensure we can update the default Sale object.
        """
        url = '/api/sale/{}/'.format(self.sale.id)
        data = {
            "url": "http://127.0.0.1:8000/api/sale/{}/".format(self.sale.id),
            "channel": [
                "http://127.0.0.1:8000/api/sales_channel/InStore/"
            ],
            "store": "http://127.0.0.1:8000/api/store/FOO1/",
            "docket_number": 2,
            "datetime": "2018-02-04T00:40:44.313123Z",
            "status": "complete",
            "amount": "1.15",
            "amount_excl": "1.00",
            "discount": "0.00",
            "tax": "0.15",
            "customer_id": None,
            "identification_id": None,
            "pos_id": None,
            "staff_id": None,
            "tenders": [],
            "sale_items": []}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_full_store(self):
        """
        Ensure we can create a new empty Sale object but using the full representation of the store.
        """
        url = '/api/sale/'
        data = {
            "channel": [
                "http://127.0.0.1:8000/api/sales_channel/InStore/"
            ],
            "store": {
                "url": "http://127.0.0.1:8000/api/store/FOO1/",
                "name": "foo changed"
            },
            "docket_number": 3,
            "datetime": "2018-02-04T00:40:44.313123Z",
            "total_amount": "0.00",
            "tenders": [],
            "sale_items": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sale_with_sub_objects(self):
        url = '/api/sale/'
        data = {
            "type": "Sale",
            "channel": [
                "http://127.0.0.1:8000/api/sales_channel/InStore/"
            ],
            "datetime": "2018-03-19T04:02:23Z",
            "store": "http://127.0.0.1:8000/api/store/FOO1/",
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
