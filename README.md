# drf-nest
Writable nested serialisers for Django Rest Framework

## To run sample project

```shell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser super super@super.com super
python manage.py runserver
```

## To use

```shell
python setup.py install
```

In your serialisers.py file import extensions:

```python
from drf_nest.serializers import ExtendedHyperlinkedSerialiser
from drf_nest.serializer_fields import ExtendedModelSerialiserField
```

For each model serialiser using nested field use the ExtendedHyperlinkedSerialiser

```python
class SaleSerialiser(ExtendedHyperlinkedSerialiser):
```

For each nested representation in the parent object use the ExtendedModelSerialiserField

```python
    sale_items = ExtendedModelSerialiserField(
        SaleItemSerialiser(), 
        many=True, 
        required=False, 
        allow_null=True)
```

We won't know the parents relationship on create so in each sub objects serialiser, the parent object must be made optional.
```python
    sale = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='sale-detail',
        queryset=Sale.objects.all()
    )
```

## Playing With the sample project:

Create some required base objects for the sample project:
```json
{
    "type": "SalesChannel",
    "url": "http://127.0.0.1:8000/api/sales_channel/test_channel/",
    "name": "test_channel"
}
```
```json
{
    "type": "TenderType",
    "url": "http://127.0.0.1:8000/api/tender_type/Cash/",
    "name": "Cash",
    "description": ""
}
```

Sample create payload to POST a new sale:
```json
{
    "type": "Sale",
    "channel": "http://127.0.0.1:8000/api/sales_channel/test_channel/",
    "store_code": "S1",
    "datetime": "2018-03-19T04:02:23Z",
    "docket_number": 1,
    "status": "complete",
    "amount": "1.15",
    "amount_excl": "1.00",
    "discount": "0.00",
    "tax": "0.15",
    "customer_id": null,
    "identification_id": null,
    "pos_id": null,
    "staff_id": null,
    "tenders": [
        {
            "type": "Tender",
            "tender_type": "http://127.0.0.1:8000/api/tender_type/Cash/",
            "amount": "1.15",
            "reference": null
        }
    ],
    "sale_items": [
        {
            "type": "SaleItem",
            "product_offering_id": "1",
            "supplier_product_id": "1",
            "product_name": "Test Product",
            "status": "sold",
            "status_related_sale": null,
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
```
