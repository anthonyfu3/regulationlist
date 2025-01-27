from django.db import models
from django.contrib.auth.models import User

class ListItem(models.Model):
    number_in_list = models.AutoField(primary_key=True)  # Auto-increment ID
    name = models.CharField(max_length=255, default="Unnamed Item")  # Name of the item with a default value
    description = models.TextField()  # Item description
    is_valid = models.BooleanField(default=None, null=True, blank=True)  # None for undecided, True/False for valid/not valid
    votes_needed = models.PositiveIntegerField()  # Total number of votes required (can be based on number of judges)
    votes_had = models.PositiveIntegerField(default=0)  # Count of total votes received
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')  # ListMaker

    def __str__(self):
        return f"{self.number_in_list}: {self.name[:30]}"

    @property
    def vote_status(self):
        if self.is_valid is None:
            return "Pending"
        return "Valid" if self.is_valid else "Not Valid"
