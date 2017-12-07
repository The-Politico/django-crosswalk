from django.core.exceptions import ValidationError

reserved_keys = ['entity', 'created', 'match_score']


def validate_shallow_dict(value):
    """Only allow shallow dictionaries."""
    if isinstance(value, dict):
        for key in value:
            if isinstance(value[key], dict):
                raise ValidationError("Nested attributes are not allowed.")
            if key in reserved_keys:
                raise ValidationError("Reserved key detected in attributes.")
