from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Good
from .serializers import GoodSerializer
from .permissions import IsSellerOrReadOnly

class GoodViewSet(viewsets.ModelViewSet):
    queryset = Good.objects.all().order_by('-created_at')
    serializer_class = GoodSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the seller to the user making the request
        serializer.save(seller=self.request.user)

