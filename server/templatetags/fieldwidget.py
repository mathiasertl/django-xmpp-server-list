from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

register = template.Library()

@register.filter
def fieldwidget(boundfield):
    field = boundfield.field
    form = boundfield.form
    widget = field.widget
    
    if 'class' in widget.attrs and widget.attrs['class'] == 'mapwidget':
        html = boundfield.as_widget()
        static_url = settings.STATIC_URL
        if form.instance.id:
            url = reverse("server_ajax_id_mapbrowse", kwargs={'server_id': form.instance.id} )
        else:
            url = reverse('server_ajax_mapbrowse')
        
        if form.prefix:
            rel = 'id_%s-mapbrowse' % form.prefix
        else:
            rel = 'id_mapbrowse'
        
        html += """
<a href="%s"
        rel="#%s" style="text-decoration:none">
    <img src="%simg/osm.png" />
</a>
<div class="overlay" id="%s">
    <div class="contentWrap"></div>
</div>
""" % (url, rel, static_url, rel)
        return mark_safe(html)
    else:
        return boundfield