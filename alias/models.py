from django.db import models
from django.core.validators import ValidationError
import datetime

# Create your models here.


class Alias(models.Model):
    """Alias model.

    Attributes:
        alias (str): Name of an alias.
        target (str): A "soft foreign key" to slugs of other models/apps of the existing project; will never be longer than 24 characters.
        start (datetime): microsecond precision timestamp/datetime. Start of range.
        end (datetime, optional): microsecond precision timestamp/datetime or None. End of range.

    """

    alias = models.CharField(max_length=500)
    target = models.SlugField(max_length=24)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def clean(self, *args, **kwargs):
        """Checks for correct date ranges and no overlaps"""
        if self.end is not None:
            if self.end <= self.start:
                raise ValidationError("end earlier than start")
        all_aliases = Alias.objects.filter(
            target=self.target, alias=self.alias
        )
        if not self._state.adding:
            all_aliases = all_aliases.exclude(pk=self.pk)
        print(all_aliases)
        for obj in all_aliases:
            if obj.start < self.start:
                start1, start2, end1, end2 = (
                    obj.start,
                    self.start,
                    obj.end,
                    self.end,
                )
            else:
                start1, start2, end1, end2 = (
                    self.start,
                    obj.start,
                    self.end,
                    obj.end,
                )
            if end1 is None:
                end1 = start2 + datetime.timedelta(microseconds=1)
            if end2 is None:
                end2 = start2
            if start1 <= end2 and start2 < end1:
                raise ValidationError("overlapping date range")
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.alias} for {self.target} from {self.start} to {self.end}"
        )
