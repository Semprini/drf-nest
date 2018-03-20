from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Store(models.Model):
    code = models.CharField(primary_key=True, max_length=50)
    name =  models.CharField( max_length=100 )

    
class SalesChannel(models.Model):
    name =  models.CharField( primary_key=True, max_length=100 )

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return "%s"%(self.name)


class Sale(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    sale_type = models.CharField(max_length=50, choices=(('retail', 'retail'), ('cash account', 'cash account'), ('credit account', 'credit account')), default='retail')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_sales')

    channel = models.ManyToManyField(SalesChannel)
    
    datetime = models.DateTimeField(default=now)
    status = models.CharField(max_length=50, choices=(('basket', 'basket'), ('complete', 'complete')), default='complete')
    docket_number = models.IntegerField()

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_excl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    identification_id = models.CharField(max_length=50,null=True, blank=True)

    customer_id = models.CharField(max_length=50,null=True, blank=True)
    pos_id = models.CharField(max_length=50,null=True, blank=True)
    staff_id = models.CharField(max_length=50,null=True, blank=True)

    class Meta:
        ordering = ['-datetime']
        
    def __str__(self):
        return "%s|%s|%d"%(self.store.code, self.datetime, self.docket_number)
        
    def save(self, raw=False, *args, **kwargs):
        if self.id == "":
            self.id = '{}-{:04d}{:02d}{:02d}{}'.format(self.store.code, self.datetime.year, self.datetime.month, self.datetime.day, self.docket_number)
        if raw:
            self.save_base(raw=True)
        else:
            super(Sale, self).save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, db_index=True, related_name='sale_items')
    
    product_offering_id = models.CharField(max_length=50)
    supplier_product_id = models.CharField(max_length=50,null=True, blank=True)
    product_name = models.CharField(max_length=150,null=True, blank=True)
    
    status = models.CharField(max_length=200, choices=(('sold', 'sold'), ('returned', 'returned'),), default='sold')
    status_related_sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.CASCADE, db_index=True, related_name='related_sale_items')
    
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit_of_measure = models.CharField(max_length=200, choices=(('each', 'each'), ('kg', 'kg'), ('square metre', 'square metre'), ('lineal metre', 'metre')), default='each')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_excl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    retail_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']
        
    def __str__(self):
        return "%s|%s|%d"%(self.sale.id, self.product_offering_id, self.amount)


class TenderType(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    description = models.TextField(blank=True)

    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Tender(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, db_index=True, related_name='tenders')
    tender_type = models.ForeignKey(TenderType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['id']
        
    def __str__(self):
        return "%s %s"%(self.sale, self.tender_type)



    