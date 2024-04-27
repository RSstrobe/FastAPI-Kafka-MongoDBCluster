import http

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from yarl import URL

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        payload = {"email": username, "hashed_password": password}
        # TODO: add for jaeger headers = {'X-Request-Id': str(uuid.uuid4())}
        # TODO: add secure data in `-d`
        url = str(URL(settings.AUTH_API_LOGIN_URL).with_query(payload))
        # TODO: Подумать над graceful degradationq
        try:
            response = requests.post(url)
        except Exception:  # TODO: Лучше вылавливать конкретные ошибки
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        url_verify_user = str(
            URL(settings.AUTH_API_VERIFY_ROLE_URL).with_query(
                {"email": username, "role_name": "Admin"}
            )
        )
        response = requests.post(
            url_verify_user,
            cookies={"access_token": response.cookies.get("access_token")},
        )
        is_admin = False
        if response.status_code == http.HTTPStatus.OK:
            is_admin = True

        try:
            user, created = User.objects.get_or_create(email="admin@admin.ru")
            user.email = username
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.is_admin = is_admin
            user.is_active = True
            user.is_staff = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
