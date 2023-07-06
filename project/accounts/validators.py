import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PassValidator:
    password_regex = re.compile(
        r"""^(?=.*?[A-Z])  # check 1 or more A-Z symbol
                                    (?=.*?[0-9])  # check 1 or more 0-9 symbol
                                    [0-9a-zA-Z!?@#$%^&*()\[\]{}<>,._'\-+=|/]  # valid symbols in password
                                    {8,15}  # valid password length""",
        re.X,
    )

    def validate(self, password, user=None):
        if not self.password_regex.fullmatch(password):
            raise ValidationError(
                _(
                    " От 8 до 15 символов, 1 заглавная латинская буква и 1 цифра. "
                    "Допускаются только латинские буквы, цифры и следующие знаки: !?@#$%^&*()[]{}<>,._'-+=|/"
                ),
                code="wrong password",
            )

    def get_help_text(self):
        return _(
            " От 8 до 15 символов, 1 заглавная латинская буква и 1 цифра. "
            "Допускаются только латинские буквы, цифры и следующие знаки: !?@#$%^&*()[]{}<>,._'-+=|/"
        )
