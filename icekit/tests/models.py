"""
Test models for ``icekit`` app.
"""
from django.db import models
from django.http import HttpResponse

from fluent_pages.extensions import page_type_pool

from icekit import abstract_models
from icekit.articles.abstract_models import ListingPage, ArticleBase
from icekit.articles.page_type_plugins import ListingPagePlugin
from icekit.page_types.layout_page.abstract_models import \
    AbstractLayoutPage, AbstractUnpublishableLayoutPage
from icekit.plugins import ICEkitFluentContentsPagePlugin


class BaseModel(abstract_models.AbstractBaseModel):
    """
    Concrete base model.
    """
    pass


class FooWithLayout(abstract_models.LayoutFieldMixin):
    pass


class BarWithLayout(abstract_models.LayoutFieldMixin):
    pass


class BazWithLayout(abstract_models.LayoutFieldMixin):
    pass


class ImageTest(models.Model):
    image = models.ImageField(upload_to='testing/')


class ArticleListing(ListingPage):
    """A page that lists articles that link to it as parent"""

    def get_items(self):
        unpublished_pk = self.get_draft().pk
        return Article.objects.published().filter(parent_id=unpublished_pk)

    def get_visible_items(self):
        unpublished_pk = self.get_draft().pk
        return Article.objects.visible().filter(parent_id=unpublished_pk)

    class Meta:
        db_table = 'test_articlelisting'


class Article(ArticleBase):
    """Articles that belong to a particular listing"""
    parent = models.ForeignKey(ArticleListing)

    class Meta:
        db_table = 'test_article'

    def get_response(self, request, parent=None, *args, **kwargs):
        return HttpResponse(
            u"%s: %s" % (self.parent.get_published().title, self.title)
        )

class LayoutPageWithRelatedPages(AbstractLayoutPage):
    related_pages = models.ManyToManyField('fluent_pages.Page')

    class Meta:
        db_table = 'test_layoutpage_with_related'


@page_type_pool.register
class LayoutPageWithRelatedPagesPlugin(ICEkitFluentContentsPagePlugin):
    """
    LayoutPage implementation as a plugin for use with pages.
    """
    model = LayoutPageWithRelatedPages
    render_template = 'icekit/page_types/article/default.html'


class UnpublishableLayoutPage(AbstractUnpublishableLayoutPage):
    pass


@page_type_pool.register
class UnpublishableLayoutPagePlugin(ICEkitFluentContentsPagePlugin):
    model = UnpublishableLayoutPage
    render_template = 'icekit/layouts/default.html'


@page_type_pool.register
class ArticleListingPlugin(ListingPagePlugin):
    model = ArticleListing
