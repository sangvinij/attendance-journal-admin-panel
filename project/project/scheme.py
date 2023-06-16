from drf_spectacular.extensions import OpenApiAuthenticationExtension
from django.conf import settings


class KnoxTokenScheme(OpenApiAuthenticationExtension):
    target_class = 'knox.auth.TokenAuthentication'
    name = 'knoxTokenAuth'
    match_subclasses = True
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': settings.SESSION_COOKIE_NAME,
        }


def custom_preprocessing_hook(endpoints):
    hidden_urls = {'/auth/users/activation/',
                   '/api/users/study_fields/{pk}/',
                   '/api/users/list/{pk}/',
                   '/auth/users/',
                   '/auth/users/{id}/',
                   '/auth/users/resend_activation/',
                   '/auth/users/reset_password/',
                   '/auth/users/reset_password_confirm/',
                   '/auth/users/reset_username_confirm/',
                   '/auth/users/reset_username/',
                   '/auth/users/set_username/',
                   '/auth/users/set_password/', }
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        if path not in hidden_urls:
            filtered.append((path, path_regex, method, callback))
    return filtered
