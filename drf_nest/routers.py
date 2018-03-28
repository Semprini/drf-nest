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

        
class AppRouter(routers.DefaultRouter):
    APIRootView = RootView
    apps = {}
    
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
