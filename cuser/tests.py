import sys

from django.conf.urls import patterns
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse
from django.test import TestCase

from cuser.fields import CurrentUserField
from cuser.middleware import CuserMiddleware


User = get_user_model()


class TestModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = CurrentUserField(
        add_only=True,
        blank=True,
        null=True,
        related_name="tests_created"
    )


class TestModel2(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.IntegerField()


def test_view(request):
    user = CuserMiddleware.get_user()

    return HttpResponse(user and user.username or "")


class CuserTestCase(TestCase):
    urls = patterns(
        '',
        (r"^test-view/", test_view, {}, "test-view"),
    )

    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@example.com",
            password="test"
        )

    def test_cuser_middleware(self):
        response = self.client.get("/test-view/")
        if sys.version < '3':
            self.assertEqual(response.content, "")
        else:
            self.assertEqual(response.content, b"")

        self.client.login(username="test", password="test")
        response = self.client.get("/test-view/")

        if sys.version < '3':
            self.assertEqual(response.content, "test")
        else:
            self.assertEqual(response.content, b"test")

    def test_current_user_field(self):
        user = User.objects.get(username="test")
        CuserMiddleware.set_user(user)
        TestModel.objects.create(name="TEST")
        CuserMiddleware.del_user()
        test_instance = TestModel.objects.get(name="TEST")

        self.assertEqual(test_instance.creator, user)

    def test_current_user_field_with_no_active_user(self):
        CuserMiddleware.del_user()
        TestModel.objects.create(name="TEST")
        test_instance = TestModel.objects.get(name="TEST")

        self.assertEqual(test_instance.creator, None)
