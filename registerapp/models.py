from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    nombre = models.CharField(max_length=100)
    crossdock = models.BooleanField()
    wharehousing = models.BooleanField()
    active = models.BooleanField()
    correo = models.BooleanField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ' - ' + self.company.nombre