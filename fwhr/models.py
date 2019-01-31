from django.db import models
from django.utils import timezone

class Image(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField()
    gender = models.CharField(max_length=10)
    age = models.IntegerField(default=20)
    fwhr = models.FloatField(default=0.)
    country = models.CharField(max_length=10)

    def __str__(self):
        return str(self.age)+", "+self.gender+", "+ self.country + ", "+ str(self.fwhr)
