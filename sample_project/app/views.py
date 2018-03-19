from rest_framework import permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from sample_project.app.models import Sale, SaleItem, Tender, TenderType, SalesChannel
from sample_project.app.serializers import SaleSerialiser, SaleItemSerialiser, TenderSerialiser, TenderTypeSerialiser, SalesChannelSerialiser


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )
   
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('channel','store_code','account_id','customer_id','job_id','identification_id','pos_id','staff_id')

            
class SalesChannelViewSet(viewsets.ModelViewSet):
    queryset = SalesChannel.objects.all()
    serializer_class = SalesChannelSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )

        
class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )

    
class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )

    
class TenderTypeViewSet(viewsets.ModelViewSet):
    queryset = TenderType.objects.all()
    serializer_class = TenderTypeSerialiser
    permission_classes = (permissions.DjangoModelPermissions, )

    