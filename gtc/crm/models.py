from django.db import models


class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=60)
    headshot_img = models.ImageField(upload_to='clients_headshot_img', null=True,
                                     blank=True)

    def __str__(self) -> str:
        """str: Get object name in human readable style."""
        return '{} {}'.format(self.first_name, self.last_name)