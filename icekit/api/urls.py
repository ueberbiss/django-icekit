import logging

from django.conf import settings
from django.conf.urls import url, include
from django.utils.module_loading import import_string
from django.contrib.auth import views as auth_views

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from icekit.project.urls import auth_urlpatterns

from .images import views as images_views
from .pages import views as pages_views
from .media_category import views as media_category_views

logger = logging.getLogger(__name__)


schema_doc_view = get_swagger_view(title='GLAMkit API')

# Obtain the default router and register local APIs
router = routers.DefaultRouter()
router.register(r'image', images_views.ImageViewSet, 'image-api')
router.register(r'page', pages_views.PageViewSet, 'page-api')
router.register(r'media-category', media_category_views.MediaCategoryViewSet, 'media-category-api')

# Register pluggable API routers defined elsewhere
for api_section_name, pluggable_router \
        in getattr(settings, 'EXTRA_API_ROUTERS', []):
    if isinstance(pluggable_router, basestring):
        try:
            pluggable_router = import_string(pluggable_router)
        except ImportError, ex:
            logger.warn(
                "Failed to load API router '%s' from EXTRA_API_ROUTERS: %s"
                % (pluggable_router, ex))
            raise
    for prefix, viewset, basename in pluggable_router.registry:
        if api_section_name:
            prefix = api_section_name + prefix
        router.register(prefix, viewset, basename)

# Define the URL patterns based upon the default router config.
urlpatterns = [
    # Autogenerated Swagger/OpenAPI docs
    url(r'^docs/', schema_doc_view),
    url(r'^', include(router.urls, namespace='api', app_name='icekit-api')),
    # Implement login/logout auth views to simplify use of Session-based
    # authentication in web browsers. We must duplicate these in the API
    # app for when it is exposed at an api.HOSTNAME subdomain with django-hosts
    # instead of appearing at a standard URL path like /api/.
    url(r'^', include(auth_urlpatterns)),
]
