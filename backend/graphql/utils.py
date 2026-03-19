from django.forms.utils import ErrorDict


def format_form_errors(errors: ErrorDict) -> dict[str, list[str]]:
    return {
        field: [e.get("message", str(e)) for e in errs]
        for field, errs in errors.get_json_data().items()
    }
