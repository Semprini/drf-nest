from django.dispatch import receiver
from django.http import HttpRequest

from rest_framework.request import Request
from rest_framework.renderers import JSONRenderer

import pika

from django.conf import settings


def notify_extra_args(serializer, exchange_prefix, exchange_header_list, *args, **kwargs):
    def inner1(f, *args, **kwargs):
        def inner2(sender, instance, raw, **kwargs):
            f(sender, instance, raw, serializer=serializer, exchange_prefix=exchange_prefix, exchange_header_list=exchange_header_list, **kwargs)
        return inner2
    return inner1
    

def serializer_context():
    request = HttpRequest()
    request.META['SERVER_NAME'] = settings.MQ_FRAMEWORK['HTTP_REST_CONTEXT']['SERVER_NAME']
    request.META['SERVER_PORT'] = settings.MQ_FRAMEWORK['HTTP_REST_CONTEXT']['SERVER_PORT']
    if settings.MQ_FRAMEWORK['HTTP_REST_CONTEXT']['SERVER_PROTOCOL'] == 'https':
        request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
    return { 'request': Request(request), }
    
    
def notify_save_instance(sender, instance, raw, created, serializer, exchange_prefix, exchange_header_list, **kwargs):
    """
    Generic notification of object change
    """
    if raw:
        return
        
    # To allow related objects to be sent in signal we can set a dictionary of things to save before the serializtion occurs
    if hasattr(instance,"pre_signal_xtra_related"):
        for key, value in instance.pre_signal_xtra_related.items():
            if type(value[0]) == list:
                for item in value[0]:
                    setattr( item, value[1], instance )
                    item.save()
            else:
                setattr( value[0], value[1], instance )
                value[0].save()
                
    if created:
        exchange_name = exchange_prefix + ".created"
    else:
        exchange_name = exchange_prefix + ".updated"

    headers_dict = {}
    for header in exchange_header_list:
        headers_dict[header] = '%s'%getattr(instance,header)
            
    json = JSONRenderer().render(serializer(instance, context=serializer_context()).data).decode(encoding='utf-8')

    if settings.MQ_FRAMEWORK['HOST'] == 'None':
        pass
        #print("EXCHANGE=%s | HEADERS=%s"%(exchange_name, headers_dict))
        #print('%s'%json)
    else:
        credentials = pika.PlainCredentials(settings.MQ_FRAMEWORK['USER'], settings.MQ_FRAMEWORK['PASSWORD'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MQ_FRAMEWORK['HOST'],credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='headers')

        channel.basic_publish(  exchange=exchange_name,
                                routing_key='cbe',
                                body=json,
                                properties = pika.BasicProperties(headers=headers_dict))
        connection.close()    
