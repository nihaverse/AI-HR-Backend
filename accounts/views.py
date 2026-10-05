from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "name": request.user.get_full_name(),
            "email": request.user.email,
            "role": request.user.role,
        })