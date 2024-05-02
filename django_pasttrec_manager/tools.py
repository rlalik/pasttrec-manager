import json


def safe_serialize(obj):
    """
    Converts dictrionary to serializable form which skip non-serialziable objects.

    Paramaters:
    -----------
    obj : dict
        The dictionary to be serialzied

    Returns:
    --------
        The seialized string.
    """
    def default(o):
        return f"<<non-serializable: {type(o).__qualname__}>>"

    return json.dumps(obj, indent=4, default=default)


def disable_form_fields(form, disabled_fields: tuple = None, enabled_fields: tuple = None):
    """
    Disables fields of form.

    Parameters:
    -----------
    form : django.form
        The form to be processed
    disabled_fields: tuple or list
        List of to be disabled fields, mutually exclusive with 'enabled_fields'
    enabled_fields: tuple or list
        List of to not be disabled fields, mutually exclusive with 'disabled_fields'
    """

    if disabled_fields is None and enabled_fields is None:
        raise RuntimeError("Either 'disabled_fields' or 'enabled_fields' must be used.")
    if disabled_fields is not None and enabled_fields is not None:
        raise RuntimeError("Only of one 'disabled_fields' and 'enabled_fields' must be used.")

    for k, f in form.fields.items():
        if disabled_fields is not None and k in disabled_fields:
            form.fields[k].disabled = True
        if enabled_fields is not None and k not in enabled_fields:
            form.fields[k].disabled = True
