from django.db import models


class City(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=120)
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='districts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['city', 'name'], name='unique_city_district_name')
        ]

    def __str__(self):
        return f'{self.city.name} / {self.name}'
