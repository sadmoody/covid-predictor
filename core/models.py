from django.db import models
import datetime

class Entry(models.Model):
    date = models.DateField(default=datetime.date.today)
    value = models.IntegerField()

class Formula(models.Model):
    a = models.DecimalField(max_digits=15, decimal_places=5)
    b = models.DecimalField(max_digits=15, decimal_places=5)
    c = models.DecimalField(max_digits=15, decimal_places=5)
    d = models.DecimalField(max_digits=15, decimal_places=5)

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    t_zero = models.DateField(default=datetime.date.today)
    confirmed = models.ManyToManyField(Entry, related_name="%(class)s_confirmed")
    confirmed_formula = models.ForeignKey(Formula, on_delete=models.CASCADE, null=True, related_name="%(class)s_country_confirmed")
    death = models.ManyToManyField(Entry, related_name="%(class)s_death")
    death_formula = models.ForeignKey(Formula, on_delete=models.CASCADE, null=True, related_name="%(class)s_country_death")
    long = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)

    def latest_confirmed_count(self):
        latest_confirmed_entry = self.confirmed.latest('date')
        if (latest_confirmed_entry is not None):
            return latest_confirmed_entry.value
        else:
            return 0

    def latest_death_count(self):
        latest_death_entry = self.death.latest('date')
        if (latest_death_entry is not None):
            return latest_death_entry.value
        else:
            return 0