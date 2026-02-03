from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers_auth import LoginSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            # 401 para credenciales inválidas
            return Response(ser.errors, status=status.HTTP_401_UNAUTHORIZED)

        user = ser.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "name": getattr(user, "name", "") or getattr(user, "first_name", "") or user.email,
                    "role": getattr(user, "role", ""),
                    "document_type": getattr(user, "document_type", "None"),
                    "document_number": getattr(user, "document_number", "None"),
                    "document_id": getattr(user, "document_id", ""),
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )
