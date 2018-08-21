from django.db import models


class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=60)
    headshot_img = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self) -> str:
        """str: Get object name in human readable style."""
        return '{}: {} {}'.format(self.id, self.first_name, self.last_name)

    def update_field(self, key, value):
        if key.lower() == 'id' or key.lower() == 'pk':
            raise AttributeError('{} can\'t be changed.'.format(key))
        getattr(self, key)
        setattr(self, key, value)
