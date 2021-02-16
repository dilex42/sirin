from .models import Alias
from django.core.validators import ValidationError
from django.db import transaction


def get_aliases(target, from_date, to_date):
    """Returns a set of aliases for specific target in specific datetime range.

    Args:
        target (str): Target slug for aliases to find.
        from_date (datetime or str): Start datetime for range.
        to_date (datetime or str): End datetime for range.

    Returns:
        List of found aliases.
    """
    return Alias.objects.filter(
        target=target, start__gte=from_date, end__lte=to_date
    )


@transaction.atomic
def alias_replace(existing_alias, replace_at, new_alias_value):
    """Replaces an existing alias with a new one at a specific time point.

    Args:
        existing_alias (Alias): Alias to replace.
        replace_at (datetime or str): Time point at which to replace alias.
        new_alias_value (str): Name for new Alias.

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    try:
        obj = existing_alias
        obj.end = replace_at
        obj.save()
        Alias.objects.create(
            alias=new_alias_value,
            target=obj.target,
            start=replace_at,
            end=None,
        )
        return True
    except ValidationError:
        return False
