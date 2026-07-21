from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.catalog.models import Service
from .serializers import ServiceSerializer


@api_view(["GET"])
def api_root(request):
    return Response({
        "message": "SMES API Root",
        "services": "/api/services/",
    })


@api_view(["GET"])
def service_list(request):
    services = Service.objects.all()
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)