# TODO: Remove

from django.forms.utils import ErrorDict


def format_form_errors(errors: ErrorDict) -> dict[str, list[str]]:
    return {
        field: [e["message"] for e in errs]
        for field, errs in errors.get_json_data().items()
    }
