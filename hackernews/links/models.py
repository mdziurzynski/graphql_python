from django.db import models


class Link(models.Model):
    url = models.URLField()
    description = models.TextField(null=True, blank=True)
    posted_by = models.ForeignKey('users.User', null=True, on_delete=models.deletion.CASCADE)

    @property
    def vote_count(self):
        res = self.votes.all()
        return len(res)


class Vote(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.deletion.CASCADE)
    link = models.ForeignKey('links.Link', related_name='votes', on_delete=models.deletion.CASCADE)