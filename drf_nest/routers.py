from typing import Dict
from collections import OrderedDict

from rest_framework import routers


class RootView(routers.APIRootView):
    """
    RootView
    """
    name = ""
    desc = ""
    
    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs.pop('name')
        if 'desc' in kwargs:
            self.name = kwargs.pop('desc')
        super(RootView, self).__init__(*args, **kwargs)
    
    def get_view_name(self):
        """
        Return the view name, as used in OPTIONS responses and in the
        browsable API.
        """
        return self.name

    def get_view_description(self, html=False):
        """
        Return some descriptive text for the view, as used in OPTIONS responses
        and in the browsable API.
        """
        return self.desc


class NestedRegistryItem:
    """
    Nicked from rest framework extensions
    """
    def __init__(self, router, parent_prefix, parent_item=None, parent_viewset=None):
        self.router = router
        self.parent_prefix = parent_prefix
        self.parent_item = parent_item
        self.parent_viewset = parent_viewset

    def register(self, prefix, viewset, basename, parents_query_lookups):
        self.router._register(
            prefix=self.get_prefix(
                current_prefix=prefix,
                parents_query_lookups=parents_query_lookups),
            viewset=viewset,
            basename=basename,
        )
        return NestedRegistryItem(
            router=self.router,
            parent_prefix=prefix,
            parent_item=self,
            parent_viewset=viewset
        )

    def get_prefix(self, current_prefix, parents_query_lookups):
        return '{0}/{1}'.format(
            self.get_parent_prefix(parents_query_lookups),
            current_prefix
        )

    def get_parent_prefix(self, parents_query_lookups):
        prefix = '/'
        current_item = self
        i = len(parents_query_lookups) - 1
        while current_item:
            parent_lookup_value_regex = getattr(
                current_item.parent_viewset, 'lookup_value_regex', '[^/.]+')
            prefix = '{parent_prefix}/(?P<{parent_pk_kwarg_name}>{parent_lookup_value_regex})/{prefix}'.format(
                parent_prefix=current_item.parent_prefix,
                parent_pk_kwarg_name=parents_query_lookups[i],
                parent_lookup_value_regex=parent_lookup_value_regex,
                prefix=prefix
            )
            i -= 1
            current_item = current_item.parent_item
        return prefix.strip('/')

    
class NestedRouterMixin:
    """
    Nicked from rest framework extensions
    """
    def _register(self, *args, **kwargs):
        return super().register(*args, **kwargs)

    def register(self, *args, **kwargs):
        self._register(*args, **kwargs)
        return NestedRegistryItem(
            router=self,
            parent_prefix=self.registry[-1][0],
            parent_viewset=self.registry[-1][1]
        )
        
        
class AppRouter(routers.DefaultRouter):
    APIRootView = RootView
    apps: Dict[str,str] = {}
    
    def __init__(self, *args, **kwargs):
        
        if 'root_view_name' in kwargs:
            self.root_view_name = kwargs.pop('root_view_name')
        if 'apps' in kwargs:
            self.apps = kwargs.pop('apps')
        
        super(AppRouter, self).__init__(*args, **kwargs)
        
    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_root_dict = OrderedDict()
        for key, value in self.apps.items():
            api_root_dict[key] = value
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
            
        return self.APIRootView.as_view(api_root_dict=api_root_dict,name=self.root_view_name)


class NestedAppRouter( NestedRouterMixin, AppRouter ):
    pass
    