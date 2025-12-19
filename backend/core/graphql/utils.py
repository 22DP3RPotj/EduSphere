from django.forms import BaseForm

def format_form_errors(form: BaseForm) -> dict[str, list[str]]:
    return {
        field: [e["message"] for e in errs]
        for field, errs in form.errors.get_json_data().items()
    }
