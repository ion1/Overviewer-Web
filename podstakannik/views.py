from models import Page, PageAddForm, PageEditForm
from reversion.models import Version
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings

# map from ext to (name, mime)
default_extensions = {
    'html' : ('xhtml', 'application/xhtml+xml'),
    'txt' : ('txt', 'text/plain'),
}
default_extension = 'html'

def canonicalize_url(url, def_ext=''):
    url = filter(lambda s: s != '', url.split('/'))
    url = '/' + '/'.join(url)
    
    if '.' in url:
        url, ext = url.split('.', 1)
    else:
        ext = def_ext
    
    return url, ext

def page(request, url):
    def_ext = getattr(settings, 'PODSTAKANNIK_DEFAULT_EXTENSION', default_extension)
    extensions = getattr(settings, 'PODSTAKANNIK_EXTENSIONS', default_extensions)
    url, ext = canonicalize_url(url, def_ext)
    if not ext in extensions:
        raise Http404
    
    if 'revision' in request.GET:
        try:
            revision = int(request.GET['revision'])
        except:
            raise Http404
        
        ver = get_object_or_404(Version, revision=revision)
        p = ver.get_object_version().object
    else:
        p = get_object_or_404(Page, url=url)
    
    extmap = []
    for other_ext in extensions:
        element = {}
        element['current'] = (other_ext == ext)
        element['name'] = extensions[other_ext][0]
        element['url'] = p.get_absolute_url() + '.' + other_ext
        extmap.append(element)
    
    mime = extensions[ext][1]
    
    return render_to_response('podstakannik/page.' + ext, {'page' : p, 'alternates' : extmap}, mimetype=mime)

def edit(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    preview = None
    
    if request.method == 'POST':
        form = PageEditForm(request.POST, instance=p)
        if form.is_valid():
            if 'preview' in request.POST:
                preview = form.cleaned_data['body']
            else:
                # save the valid data
                p = form.save(user=request.user)
                return HttpResponseRedirect(p.get_absolute_url())
    else:
        form = PageEditForm(instance=p)
    
    return render_to_response('podstakannik/edit.html', {'form' : form, 'page' : p, 'preview' : preview}, context_instance=RequestContext(request))

def history(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    
    history = Version.objects.get_for_object(p).reverse()
    
    return render_to_response('podstakannik/history.html', {'page' : p, 'history' : history})
