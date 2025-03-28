# utils.py
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Handle logo path
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
    
    pdf = pisa.pisaDocument(
        html,
        dest=result,
        encoding='UTF-8',
        link_callback=lambda uri, _: os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def fetch_resources(uri, rel):
    """
    Callback to allow xhtml2pdf/reportlab to retrieve images, stylesheets, etc.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = None

    return path