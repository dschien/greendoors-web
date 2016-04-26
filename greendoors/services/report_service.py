from collections import defaultdict
import logging

from django.core.urlresolvers import reverse
from django.template import Context
from django.template.defaulttags import register
from django.template.loader import get_template

from api.models import TrackableURL, RedirectUrl


__author__ = 'schien'

logger = logging.getLogger(__name__)

from django import template


def render_template(template, **kwargs):
    track_template = get_template(template)
    text = track_template.render(Context(kwargs))
    return text


# @register.simple_tag
@register.tag(name="trackurl")
def do_trackurl(parser, token):
    """
    Format is {% trackurl 'http://www.google.de' user <display_text> %}
    """
    try:
        # split_contents() knows not to split quoted strings.
        display_text = None
        contents = token.split_contents()
        if len(contents) == 3:
            tag_name, url, display_text = contents
            display_text = display_text.strip("'")
        else:
            tag_name, url = contents
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (url[0] == url[-1] and url[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's url argument should be in quotes" % tag_name)
    return TrackUrlNode(url[1:-1], display_text)


class TrackUrlNode(template.Node):
    def __init__(self, url, display_text=None, mode='link'):
        self.url = url
        self.mode = mode
        if display_text:
            self.display_text = display_text

    def render(self, context):
        return self.create_trackurl(context)

    def create_trackurl(self, context):
        """
        Create a trackable url including redirect instance for a given user and inserts a
        redirect url in its place.
        If a trackable url of this name already exist, then a redirect url for that instance is returned.
        Otherwise a new trackable url is created first.

        """
        t_url, created = TrackableURL.objects.get_or_create(url=self.url)
        t_url.save()

        # key = generate_url_key()
        redirect, created = RedirectUrl.objects.get_or_create(user=context['user'], target_url=t_url)
        if created:
            redirect.save()

        text = self.url
        if hasattr(self, 'display_text') and self.display_text is not None:
            text = self.display_text
        else:
            text = self.url
        if self.mode == 'link':
            return "<a href='{0}' target='_blank'>{1}</a>".format(reverse('api_redirect', kwargs={'key': redirect.redirect_key}), text)
        else:
            return reverse('api_redirect', kwargs={'key': redirect.redirect_key})


@register.tag(name="trackurl-raw")
def do_trackurl(parser, token):
    """
    Format is {% trackurl 'http://www.google.de' user <display_text> %}
    """
    try:
        # split_contents() knows not to split quoted strings.
        display_text = None
        contents = token.split_contents()
        tag_name, url = contents
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (url[0] == url[-1] and url[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's url argument should be in quotes" % tag_name)
    return TrackUrlNode(url[1:-1], mode='raw')


class ReportService(object):
    def get_html_report(self, **kwargs):
        """
        A report consists of :
         - a header
         - optional 'renewables' section
         - a table for each measure with
            - one row for each house where this measure was scanned with
                - text, supplier, cost, disruption
            - a paragraph with general info for the measure
         - notes, order by house
         - closing remarks
         - easy fixes
         - final word

        """
        template_name = 'report.html'
        if 'template' in kwargs:
            template_name = kwargs['template']

        report_template = get_template(template_name)
        user = kwargs['user']
        app_name = 'frome2014'
        if 'app_name' in kwargs:
            app_name = kwargs['app_name']

        scans = getattr(user, app_name + '_scan')

        measures = defaultdict(set)
        # measures = MultiValueDict()

        has_renewable = False
        houses = set()
        final_thoughts = {}

        for scan in scans.all():
            house = scan.house
            houses.add(house)

            if int(scan.text[5:8]) > 0:
                imeasure = scan.measure
                measure = imeasure.measure

                measures[measure].add(imeasure)
                if measure.category.is_renewable:
                    has_renewable = True
            else:
                # all measures
                imeasures = house.measures
                for imeasure in imeasures.all():
                    measures[imeasure.measure].add(imeasure)

                    if imeasure.measure.category.is_renewable:
                        has_renewable = True

            if house.final_notes and not house.final_notes == '0':
                final_thoughts[house.pk] = house.final_notes



        notes = getattr(user, app_name + '_note').all()

        # http://stackoverflow.com/questions/4764110/django-template-cant-loop-defaultdict
        measures.default_factory = None
        # for i,j in measures.items():
        # print i
        context = Context(kwargs)

        context.update({'user': user, 'has_renewable': has_renewable, 'notes': notes,
                        'measures': measures, 'visit_count': len(houses), 'final_thoughts': final_thoughts})

        text = report_template.render(context)
        return text


