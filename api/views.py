from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_overview(request):
    api_urls = {
        'List': '/item-list/',
        'Detail View': '/item-detail/<str:pk>/',
        'Create': '/item-create/',
        'Update': '/item-update/<str:pk>/',
        'Delete': '/item-delete/<str:pk>/',
    }
    return Response(api_urls)