from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_csv.renderers import CSVRenderer

class PaginatedCSVRenderer (CSVRenderer):
    results_field = 'results'

    def render(self, data, *args, **kwargs):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(PaginatedCSVRenderer, self).render(data, *args, **kwargs)
        

class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):

    """Renders the browsable api, but excludes the forms."""

    # def get_context(self, *args, **kwargs):
    #    ctx = super().get_context(*args, **kwargs)
    #    ctx['display_edit_forms'] = False
    #    return ctx

    # def show_form_for_method(self, view, method, request, obj):
    #    """We never want to do this! So just return False."""
    #    return False

    def get_rendered_html_form(self, data, view, method, request):
        """Why render _any_ forms at all. This method should return 
        rendered HTML, so let's simply return an empty string.
        """
        return ""
