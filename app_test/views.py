from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def here(request):
    return render(request, 'app_test/here.html', {})
