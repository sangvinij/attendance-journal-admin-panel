CREATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "middle_name": {"type": ["string", "null"]},
        "is_superuser": {"type": "boolean"},
        "is_metodist": {"type": "boolean"},
        "is_teacher": {"type": "boolean"},
        "is_active": {"type": "boolean"},
        "email": {"type": "string"},
        "date_added": {"type": "string"},
        "last_update": {"type": "string"},
    },
    "required": ["id", "username", "first_name", "last_name", "email"],
}
