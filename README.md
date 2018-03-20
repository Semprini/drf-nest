# drf-nest
Writable nested serialisers for Django Rest Framework

## To run sample project

```shell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser super super@super.com super
python manage.py runserver
```
## The sample
A sample project is included which implements a retail type use case. Sales have a foreign key to a store and the sale items have foreign keys to the sale.

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
class SaleSerialiser(ExtendedHyperlinkedSerialiser):
    sale_items = ExtendedModelSerialiserField(
        SaleItemSerialiser(), 
        many=True, 
        required=False, 
        allow_null=True)
```

We won't know the foreign key to fulfill the relationship if we are creating the parent so in each sub objects serialiser, the parent object must be made optional.
```python
class SaleItemSerialiser(ExtendedHyperlinkedSerialiser):
    sale = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='sale-detail',
        queryset=Sale.objects.all()
    )
```

## How does it work
The serialiser field overrides the to internal function to return a dictionary (or list of dictionaries) rather than the django model instance.
This is done because the fields do not know if the parent exists already but may have a required foreign key constraint.

## Features

See the sample project tests for example POST requests.

 - During POST, PUT and PATCH user can specify nested object either by URL or full serialised representation
 - Adds type field to allow for generic foreign keys (in development)
 - Serialisation of model with foreign key
 - Serialisation of model with reverse relationship
 - Serialisation of model with many to many relationship
 