from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminUsersTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin@test.com", password="pass12345", role="ADMIN")
        self.gestor = User.objects.create_user(email="gestor@test.com", password="pass12345", role="GESTOR")
        self.user = User.objects.create_user(email="user@test.com", password="pass12345", role="CAMPESINO", is_active=True)

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_only_admin_can_list_users(self):
        self.auth(self.gestor)
        r = self.client.get("/api/accounts/admin/users/")
        self.assertEqual(r.status_code, 403)

        self.auth(self.admin)
        r = self.client.get("/api/accounts/admin/users/")
        self.assertEqual(r.status_code, 200)

    def test_admin_can_deactivate_and_activate_user(self):
        self.auth(self.admin)

        r = self.client.put(f"/api/accounts/admin/users/{self.user.id}/desactivar/")
        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        r = self.client.put(f"/api/accounts/admin/users/{self.user.id}/activar/")
        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
