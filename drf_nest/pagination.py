import sys
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict 

from django.core.paginator import Paginator, InvalidPage
from django.core.cache import cache

from django.core.paginator import Page


# we inherit from Page, even though it's a bit odd since we're so
# different, but if we don't some of the tools that use it will break,
# django-rest-framework for example. we do get a little bit from it though, in
# not having to implement some methods
class PerformantPage(Page):

    def __init__(self, paginator, object_list, previous_token, token,
                 next_token):
        self.paginator = paginator
        self.object_list = object_list
        self.previous_token = previous_token
        self.token = token
        self.next_token = next_token

    def __repr__(self):
        return '<PerformantPage (%s, %s %s)>' % (self.previous_token,
                                                 self.token, self.next_token)

    def has_next(self):
        return self.next_token is not None

    def has_previous(self):
        return self.previous_token is not None

    def has_other_pages(self):
        return self.has_next() or self.has_previous()

    def next_page_number(self):
        return self.next_token

    def previous_page_number(self):
        return self.previous_token

    def start_index(self):
        return None

    def end_index(self):
        return None


class PerformantPaginator(Paginator):

    def __init__(self, queryset, per_page=25, orphans=0, allow_empty_first_page=True, ordering='pk', allow_count=False):
        '''As a general rule you should ensure there's an appropriate index for
        the field provided in ordering.

        allow_count (default False) indicates whether or not to allow count
        queries that can be extremely expensive on large and fast changing
        datasets.

        allow_empty_first_page and orphans are currently ignored and only exist
        to allow dropping in place of Django's built-in pagination.
        '''
        self.queryset = queryset
        self.per_page = int(per_page)
        self.ordering = ordering
        self.allow_count = allow_count

        field = ordering.replace('-', '')
        self._reverse_ordering = field if ordering[0] == '-' else \
            '-{0}'.format(ordering)
        self._field = field
        
        super().__init__(queryset, per_page, orphans, allow_empty_first_page)

    def __repr__(self):
        return '<PerformantPaginator (%d, %s %d)>' % (self.per_page,
                                                      self.ordering,
                                                      self.allow_count)

    @property
    def count(self):
        '''Counting the number of items is expensive, so by default it's not
        supported and None will be returned.'''
        return self.queryset.count() if self.allow_count else sys.maxsize

    def default_page_number(self):
        return None

    def validate_number(self, number):
        # TODO: validate format for field type?
        return number

    def _object_to_token(self, obj):
        field = self._field
        if field == 'pk':
            value = obj._meta.pk.value_to_string(obj)
        else:
            pieces = field.split('__')
            if len(pieces) > 1:
                # traverse relationships, -1 will be our final field
                for piece in pieces[:-1]:
                    obj = getattr(obj, piece)
            # obj is now the object on which our final field lives
            value = obj._meta.get_field(pieces[-1]).value_to_string(obj)

        # return our value
        return value

    def _token_to_clause(self, token, rev=False):
        # in the forward direction we want things that are greater than our
        # value, but if the ordering is -, we want less than. if rev=True we
        # fip it
        direction = ('lt', 'gt') if rev else ('gt', 'lt')
        if self.ordering[0] == '-':
            d = direction[1]
        else:
            d = direction[0]

        field = self._field
        meta = self.queryset.model._meta
        if field == 'pk':
            value = meta.pk.to_python(token)
        else:
            pieces = field.split('__')
            if len(pieces) > 1:
                # traverse relationships, -1 will be our final field
                for piece in pieces[:-1]:
                    # grab the ForeignKey field, then its RelatedObject, which
                    # holds it's parent_model (the one at the other end of the
                    # relationship) and finally its _meta which is what we're
                    # after
                    meta = meta.get_field(piece).related.parent_model._meta

            value = meta.get_field(pieces[-1]).to_python(token.decode())

        return {'{0}__{1}'.format(self._field, d): value}

    def page(self, token=None):
        # work around generics being integer specific with a default of 1,
        # again this is to deal with some pagination consumers that force our
        # hand
        if token == 1:
            token = None

        # get a queryset
        qs = self.queryset
        # if we have a truthy token, not includeing '', we'll need to offset
        if token:
            # we're paged in a bit, token will be the values of the final
            # object of the previous page, so we'll start with it
            qs = qs.filter(**self._token_to_clause(token))

        # apply our ordering
        qs = qs.order_by(self.ordering)

        # get our object list, +1 to see if there's more to come
        object_list = list(qs[:self.per_page + 1])

        next_token = None
        # if there were more, then use
        if len(object_list) > self.per_page:
            # get rid of the extra
            object_list = object_list[:-1]
            # and now our last item's pk is the token for the next page
            next_token = self._object_to_token(object_list[-1])

        previous_token = None
        # if we have a truthy token, not including '', we'll check to see if
        # there's a prev
        if token:
            clause = self._token_to_clause(token, rev=True)
            qs = self.queryset.filter(**clause).only(self._field) \
                .order_by(self._reverse_ordering)
            try:
                previous_token = self._object_to_token(qs[self.per_page - 1])
            except IndexError:
                # can't be none b/c some tooling will turn it in to 'None'
                previous_token = ''

        # return our page
        return PerformantPage(self, object_list, previous_token, token,
                              next_token)


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

    django_paginator_class = PerformantPaginator


    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', self.page.token),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
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
                page_number=page_number, message=exc
            )
            raise NotFound(msg)

        self.display_page_controls = False

        self.request = request
        return list(self.page)    

        
class PageNumberPaginationWithCachedCount(PageNumberPagination):

    django_paginator_class = CachedPaginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', self.page.token),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

         
