import cloudinary.uploader

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Case, CaseDocument
from .permissions import CanAccessCase
from .serializers_documents import CaseDocumentSerializer, CaseDocumentUploadSerializer


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        ser = CaseDocumentUploadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        case_id = ser.validated_data["case_id"]
        category = ser.validated_data.get("category", "OTRO")
        file = ser.validated_data["file"]

        case = Case.objects.get(id=case_id)

        # 🔐 permiso por objeto (mismo que usas en solicitudes)
        perm = CanAccessCase()
        if not perm.has_object_permission(request, None, case):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        # ☁️ subir a Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=f"campesena/cases/{case.id}",
            resource_type="auto",
        )

        doc = CaseDocument.objects.create(
            case=case,
            category=category,
            file_url=result["secure_url"],
            public_id=result.get("public_id", ""),
            original_name=file.name,
            size_bytes=file.size,
            mime_type=getattr(file, "content_type", "") or "",
            uploaded_by=request.user,
        )

        return Response(
            CaseDocumentSerializer(doc, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        case_id = request.query_params.get("case_id")
        if not case_id:
            return Response({"detail": "Falta case_id"}, status=status.HTTP_400_BAD_REQUEST)

        case = Case.objects.get(id=case_id)

        perm = CanAccessCase()
        if not perm.has_object_permission(request, None, case):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        docs = CaseDocument.objects.filter(case=case).order_by("-id")
        return Response(CaseDocumentSerializer(docs, many=True, context={"request": request}).data)
