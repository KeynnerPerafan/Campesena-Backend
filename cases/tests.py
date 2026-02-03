import uuid
from unittest.mock import patch

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from cases.models import Case

User = get_user_model()


class PermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(email="admin@test.com", password="pass12345", role="ADMIN")
        self.gestor = User.objects.create_user(email="gestor@test.com", password="pass12345", role="GESTOR")
        self.camp1 = User.objects.create_user(email="camp1@test.com", password="pass12345", role="CAMPESINO")
        self.camp2 = User.objects.create_user(email="camp2@test.com", password="pass12345", role="CAMPESINO")

        self.case1 = Case.objects.create(
            applicant_type="CAMPESINO",
            request_type="CAPACITACION",
            data={"x": 1},
            created_by=self.camp1,
        )

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_can_list_cases(self):
        self.auth(self.admin)
        r = self.client.get("/api/cases/")
        self.assertEqual(r.status_code, 200)

    def test_campesino_can_see_own_case_detail(self):
        self.auth(self.camp1)
        r = self.client.get(f"/api/cases/{self.case1.id}/")
        self.assertEqual(r.status_code, 200)

    def test_campesino_cannot_see_other_case_detail(self):
        self.auth(self.camp2)
        r = self.client.get(f"/api/cases/{self.case1.id}/")
        self.assertIn(r.status_code, [403, 404])

    def test_non_admin_cannot_create_users(self):
        self.auth(self.gestor)
        r = self.client.post(
            "/api/accounts/admin/users/",
            data={"email": "x@test.com", "password": "pass12345", "role": "CAMPESINO"},
            format="json",
        )
        self.assertEqual(r.status_code, 403)


class CrearSolicitudCampesinoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.camp = User.objects.create_user(email="camp@test.com", password="pass12345", role="CAMPESINO")

    def auth(self):
        self.client.force_authenticate(user=self.camp)

    def test_post_solicitud_borrador_ok(self):
        self.auth()
        r = self.client.post(
            "/api/solicitudes/",
            data={
                "applicant_type": "CAMPESINO",
                "request_type": "CAPACITACION",
                "status": "BORRADOR",
                "uuid_externo": str(uuid.uuid4()),
                "data": {"municipio": "X", "actividad_productiva": "Y", "descripcion_idea": "Z"},
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)

    def test_post_solicitud_registrada_requires_fields(self):
        self.auth()
        r = self.client.post(
            "/api/solicitudes/",
            data={
                "applicant_type": "CAMPESINO",
                "request_type": "CAPACITACION",
                "status": "REGISTRADA",
                "data": {"municipio": "X"},  # incompleto
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)


class DocumentosTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="camp_docs@test.com", password="pass12345", role="CAMPESINO")
        self.client.force_authenticate(user=self.user)

        self.case = Case.objects.create(
            applicant_type="CAMPESINO",
            request_type="CAPACITACION",
            data={"municipio": "X"},
            created_by=self.user,
        )

    @patch("cloudinary.uploader.upload")
    def test_upload_and_list_documents(self, mock_upload):
        mock_upload.return_value = {
            "secure_url": "https://example.com/test-file.pdf",
            "public_id": f"campesena/cases/{self.case.id}/test-file",
        }

        f = SimpleUploadedFile("prueba.txt", b"hola", content_type="text/plain")

        r = self.client.post(
            "/api/documentos/subir/",
            data={"case_id": self.case.id, "category": "OTRO", "file": f},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201)
        self.assertIn("file_url", r.json())

        r2 = self.client.get(f"/api/documentos/?case_id={self.case.id}")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(r2.json()), 1)


class SyncOfflineTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="sync@test.com", password="pass12345", role="CAMPESINO")
        self.client.force_authenticate(user=self.user)

    def test_sync_creates_and_returns_mapping(self):
        u1 = str(uuid.uuid4())
        u2 = str(uuid.uuid4())

        r = self.client.post(
            "/api/sync/solicitudes/",
            data={
                "submit": True,
                "solicitudes": [
                    {"uuid_externo": u1, "applicant_type": "CAMPESINO", "request_type": "CAPACITACION", "data": {"a": 1}},
                    {"uuid_externo": u2, "applicant_type": "CAMPESINO", "request_type": "PROYECTO_PRODUCTIVO", "data": {"b": 2}},
                ],
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(u1, r.json()["mapping"])
        self.assertIn(u2, r.json()["mapping"])

    def test_sync_is_idempotent_no_duplicates(self):
        u1 = str(uuid.uuid4())

        r1 = self.client.post(
            "/api/sync/solicitudes/",
            data={"solicitudes": [{"uuid_externo": u1, "applicant_type": "CAMPESINO", "request_type": "CAPACITACION", "data": {"a": 1}}]},
            format="json",
        )
        self.assertEqual(r1.status_code, 200)

        r2 = self.client.post(
            "/api/sync/solicitudes/",
            data={"solicitudes": [{"uuid_externo": u1, "applicant_type": "CAMPESINO", "request_type": "CAPACITACION", "data": {"a": 2}}]},
            format="json",
        )
        self.assertEqual(r2.status_code, 200)

        # solo debe existir 1 case con ese uuid
        self.assertEqual(Case.objects.filter(external_uuid=u1).count(), 1)


class TimelineEventosTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="evt@test.com", password="pass12345", role="CAMPESINO")
        self.client.force_authenticate(user=self.user)

        self.case = Case.objects.create(
            applicant_type="CAMPESINO",
            request_type="CAPACITACION",
            data={"municipio": "X"},
            status="BORRADOR",
            created_by=self.user,
        )

    def test_eventos_incluye_update_y_status_change(self):
        # update borrador -> UPDATED
        r1 = self.client.patch(
            f"/api/solicitudes/{self.case.id}/",
            data={"data": {"municipio": "Y"}},
            format="json",
        )
        self.assertIn(r1.status_code, [200, 202])

        # cambio a REGISTRADA -> STATUS_CHANGED
        r2 = self.client.patch(
            f"/api/solicitudes/{self.case.id}/",
            data={"status": "REGISTRADA"},
            format="json",
        )
        self.assertIn(r2.status_code, [200, 202])

        r3 = self.client.get(f"/api/solicitudes/{self.case.id}/eventos/")
        self.assertEqual(r3.status_code, 200)

        events = r3.json()
        self.assertTrue(len(events) >= 2)


class LoginAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # crear 4 usuarios con documento + pass hasheada
        self.admin = User.objects.create_user(
            email="admin@login.com",
            password="pass12345",
            role="ADMIN",
            document_type="CC",
            document_number="1001",
        )
        self.gestor = User.objects.create_user(
            email="gestor@login.com",
            password="pass12345",
            role="GESTOR",
            document_type="CC",
            document_number="1002",
        )
        self.camp = User.objects.create_user(
            email="camp@login.com",
            password="pass12345",
            role="CAMPESINO",
            document_type="CC",
            document_number="1003",
        )
        self.asoc = User.objects.create_user(
            email="asoc@login.com",
            password="pass12345",
            role="ASOCIACION",
            document_type="NIT",
            document_number="9001",
        )

    def login_ok(self, doc_type, doc_number):
        r = self.client.post(
            "/api/auth/login/",
            data={"document_type": doc_type, "document_number": doc_number, "password": "pass12345"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("access", body)
        self.assertIn("refresh", body)
        self.assertIn("user", body)
        self.assertIn("role", body["user"])

    def test_login_admin_ok(self):
        self.login_ok("CC", "1001")

    def test_login_gestor_ok(self):
        self.login_ok("CC", "1002")

    def test_login_campesino_ok(self):
        self.login_ok("CC", "1003")

    def test_login_asociacion_ok(self):
        self.login_ok("NIT", "9001")

    def test_login_invalid_credentials(self):
        r = self.client.post(
            "/api/auth/login/",
            data={"document_type": "CC", "document_number": "1001", "password": "MAL"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)