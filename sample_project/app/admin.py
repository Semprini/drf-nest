from django.contrib import admin
from drf_nest.admin import SingleTextInputFilter

from sample_project.app.models import Sale, SaleItem, TenderType, Tender, SalesChannel, Store

class TenderInline(admin.TabularInline):
    model = Tender
    extra = 0

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    fk_name = 'sale'
    extra = 0

class SaleAdmin(admin.ModelAdmin):
    list_display = ('store', 'sale_type', 'datetime','staff_id','docket_number','amount','discount')
    list_filter = [('staff_id', SingleTextInputFilter), 'datetime', 'sale_type', 'store']
    inlines = [ TenderInline, SaleItemInline]
    readonly_fields=('id',)

    
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem)
admin.site.register(TenderType)
admin.site.register(Tender)
admin.site.register(SalesChannel)
admin.site.register(Store)
