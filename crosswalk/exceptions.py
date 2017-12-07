from django.core.exceptions import ValidationError


class ReservedKeyError(ValidationError):
    pass


class NestedAttributesError(ValidationError):
    pass
