from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class ConvocatoriasAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin@t.com", password="pass12345", role="ADMIN")
        self.camp = User.objects.create_user(email="camp@t.com", password="pass12345", role="CAMPESINO")

    def test_admin_can_create_and_list(self):
        self.client.force_authenticate(user=self.admin)

        r = self.client.post(
            "/api/admin/convocatorias/",
            data={
                "title": "Convocatoria 1",
                "description": "Desc",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
                "status": "ABIERTA",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)

        r2 = self.client.get("/api/admin/convocatorias/")
        self.assertEqual(r2.status_code, 200)

    def test_dates_validation(self):
        self.client.force_authenticate(user=self.admin)

        r = self.client.post(
            "/api/admin/convocatorias/",
            data={
                "title": "Mala fecha",
                "start_date": "2026-03-10",
                "end_date": "2026-03-01",
                "status": "ABIERTA",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)

    def test_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.camp)
        r = self.client.get("/api/admin/convocatorias/")
        self.assertEqual(r.status_code, 403)
