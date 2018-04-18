import sys
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict 


from django.core.paginator import Paginator
from django.core.cache import cache

class CachedPaginator(Paginator):
    def _get_count(self):
        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)

    
class CountlessPaginator(Paginator):
    @property
    def count(self):
        return sys.maxsize    

        
class PageNumberPaginationWithoutCount(PageNumberPagination):

    django_paginator_class = CountlessPaginator


    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', self.page.number),
            ('results', data)
        ]))
        
        
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        self.display_page_controls = False

        self.request = request
        return list(self.page)    

        
class PageNumberPaginationWithCachedCount(PageNumberPagination):

    django_paginator_class = CachedPaginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

         
                