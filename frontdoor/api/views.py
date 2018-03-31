from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'base_generic.html', context={})
    # return HttpResponse("hello")

# def getcachemoney(request):
#     return JsonResponse({'cards':[]})
