from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete
from django.conf import settings

class AppConfig(AppConfig):
    name = 'sample_project.app'

    def ready(self):
        import drf_nest.signals
        from sample_project.app.models import Sale
        from sample_project.app.serializers import SaleSerialiser

        exchange_prefix = settings.MQ_FRAMEWORK['EXCHANGE_PREFIX'] + self.name
        exchange_header_list = ('channel', 'sale_type',)
        
        post_save.connect(  drf_nest.signals.notify_extra_args(    serializer=SaleSerialiser, 
                                                                    exchange_prefix=exchange_prefix + ".Sale", 
                                                                    exchange_header_list=exchange_header_list)
                                                               (drf_nest.signals.notify_save_instance), 
                            sender=Sale, weak=False)