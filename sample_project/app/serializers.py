from urllib.parse import urlparse

from django.urls import resolve
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from drf_nest.serializers import ExtendedHyperlinkedSerialiser
from drf_nest.serializer_fields import ExtendedModelSerialiserField

from sample_project.app.models import SalesChannel, Sale, SaleItem, TenderType, Tender, Store


class StoreSerialiser(ExtendedHyperlinkedSerialiser):
    class Meta:
        model = Store
        fields = ('type', 'url', 'code', 'name', )

        
class TenderTypeSerialiser(ExtendedHyperlinkedSerialiser):
    class Meta:
        model = TenderType
        fields = ('type', 'url', 'name', 'description', )


class TenderSerialiser(ExtendedHyperlinkedSerialiser):
    sale = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='sale-detail',
        queryset=Sale.objects.all()
    )
    
    class Meta:
        model = Tender
        fields = ('type', 'url', 'sale', 'tender_type', 'amount', 'reference', )

        
class SalesChannelSerialiser(ExtendedHyperlinkedSerialiser):
    class Meta:
        model = SalesChannel
        fields = ('type', 'url', 'name',)
        
        
class SaleItemSerialiser(ExtendedHyperlinkedSerialiser):
    sale = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='sale-detail',
        queryset=Sale.objects.all()
    )

    class Meta:
        model = SaleItem
        fields = (  'type', 'url', 'sale', 'product_offering_id', 'supplier_product_id', 'product_name',
                    'status', 'status_related_sale', 'quantity', 'unit_of_measure', 
                    'amount', 'amount_excl', 'discount','tax', 'retail_price', )


class SaleSerialiser(ExtendedHyperlinkedSerialiser):
    store = ExtendedModelSerialiserField(StoreSerialiser(), required=False,)
    sale_items = ExtendedModelSerialiserField(SaleItemSerialiser(), many=True)
    tenders = ExtendedModelSerialiserField(TenderSerialiser(), many=True)
    channel = ExtendedModelSerialiserField(SalesChannelSerialiser(), many=True)
    
    class Meta:
        model = Sale
        fields = ('type', 'url', 'channel', 'store', 'datetime', 'docket_number', 'status',
                  'amount', 'amount_excl', 'discount', 'tax',
                  'customer_id', 'identification_id', 'pos_id', 'staff_id', 
                  'tenders', 'sale_items',)



