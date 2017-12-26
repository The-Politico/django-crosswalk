from crosswalk.exceptions import NestedAttributesError, ReservedKeyError


def validate_shallow_dict(value):
    """Only allow shallow dictionaries."""
    if isinstance(value, dict):
        for key in value:
            if isinstance(value[key], dict):
                raise NestedAttributesError(
                    "Nested attributes are not allowed."
                )


def validate_no_reserved_keys(value):
    reserved_keys = [
        'alias_for',
        'aliased',
        'attributes',
        'created',
        'domain',
        'entity',
        'match_score',
        'superseded_by',
        'uuid',
    ]

    if isinstance(value, dict):
        for key in value:
            if key in reserved_keys:
                raise ReservedKeyError(
                    "Reserved key in attributes."
                )


def full_validation(value):
    validate_shallow_dict(value)
    validate_no_reserved_keys(value)
