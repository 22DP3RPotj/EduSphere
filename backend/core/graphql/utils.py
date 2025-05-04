def format_form_errors(form):
    return {
        field: [e["message"] for e in errs]
        for field, errs in form.errors.get_json_data().items()
    }
