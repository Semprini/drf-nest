from rest_framework import permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from sample_project.app.models import Sale, SaleItem, Tender, TenderType, SalesChannel, Store
from sample_project.app.serializers import SaleSerialiser, SaleItemSerialiser, TenderSerialiser, TenderTypeSerialiser, SalesChannelSerialiser, StoreSerialiser


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )
   
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('channel','store','customer_id','identification_id','pos_id','staff_id')

            
class SalesChannelViewSet(viewsets.ModelViewSet):
    queryset = SalesChannel.objects.all()
    serializer_class = SalesChannelSerialiser

        
class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerialiser

    
class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerialiser

    
class TenderTypeViewSet(viewsets.ModelViewSet):
    queryset = TenderType.objects.all()
    serializer_class = TenderTypeSerialiser


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerialiser

    