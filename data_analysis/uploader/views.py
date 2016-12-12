from django.shortcuts import render
from uploader.models import UploadForm, Upload
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def home(request):
    if request.method=="POST":
        docfile = UploadForm(request.POST, request.FILES)
        if docfile.is_valid():
            docfile.save()
            return HttpResponseRedirect(reverse('document_upload'))
    else:
        docfile=UploadForm()
    files=Upload.objects.all()
    return render(request, 'uploader/home.html', {'form':docfile, 'files':files})
