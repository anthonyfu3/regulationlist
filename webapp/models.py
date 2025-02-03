from django.db import models
from django.contrib.auth.models import User

class ListItem(models.Model):
    number_in_list = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default="Unnamed Item")
    description = models.TextField()
    is_valid = models.BooleanField(default=None, null=True, blank=True)
    votes_needed = models.PositiveIntegerField()
    votes_had = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')

    def __str__(self):
        return f"{self.number_in_list}: {self.name[:30]}"

    @property
    def vote_status(self):
        if self.is_valid is None:
            return "Pending"
        return "Valid" if self.is_valid else "Not Valid"


class JudgeVote(models.Model):
    VOTE_CHOICES = [
        ('valid', 'Valid'),
        ('not valid', 'Not Valid'),
        ('pending', 'Pending'),
    ]
    list_item = models.ForeignKey(ListItem, on_delete=models.CASCADE, related_name='judge_votes')
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES, default='pending')

    class Meta:
        unique_together = ('list_item', 'judge')

    def __str__(self):
        return f"Vote for item {self.list_item.number_in_list} by {self.judge.username}: {self.vote}"
