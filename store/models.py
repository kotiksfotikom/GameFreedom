from django.db import models

class Developer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=100)
    developer = models.ForeignKey(Developer, on_delete=models.PROTECT, related_name='games')
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, related_name='games')
    genres = models.ManyToManyField(Genre, related_name='games')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateField()

    def __str__(self):
        return self.title
