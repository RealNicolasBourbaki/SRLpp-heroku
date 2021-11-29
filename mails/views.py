from django.shortcuts import render

import sys
sys.path.append('../')

from catalogue.models import SubmittedCatelogueEntries

def check_status(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None
    STATUS = {
        'in process': 'In process',
        'a': 'Accepted',
        'r': 'Rejected'
    }
    documents = [(doc, STATUS[doc.status]) for doc in SubmittedCatelogueEntries.objects.all() if doc.username == username]
    context = {'documents': documents}
    return render(request, 'check_submission_status.html', context)