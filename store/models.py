from django.db import models


class Developer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    developer = models.ForeignKey(Developer, on_delete=models.PROTECT, related_name='games')
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, related_name='games')
    genres = models.ManyToManyField(Genre, related_name='games')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    release_date = models.DateField()
    cover_image_url = models.URLField(blank=True, null=True)
    min_system_requirements = models.TextField(blank=True, null=True)
    rec_system_requirements = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title