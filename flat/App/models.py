from django.db import models


# Create your all_models here.

class Flat(models.Model):
    CHOICES_DISTRICT = (
        ("Железнодорожный", "Железнодорожный район"),
        ("Кировский", "Кировский район"),
        ("Ленинский", "Ленинский район"),
        ("Октябрьский", "Октябрьский район"),
        ("Свердловский", "Свердловский район"),
        ("Советский", "Советский район"),
        ("Центральный", "Центральный район"),
    )

    total_area = models.FloatField()
    living_area = models.FloatField()
    floor = models.IntegerField()
    district = models.CharField(choices=CHOICES_DISTRICT)
    price = models.FloatField()
