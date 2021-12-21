import os
import tarfile
import zipfile
from django.conf import settings
from django.db import models


# Create your models here.
class CatalogueEntries(models.Model):
    entry_path = models.CharField(max_length=500, default='')
    entry_name = models.CharField(max_length=100, default='')
    entry_version = models.CharField(max_length=50, default='')
    belongs_to_sub_directory = models.CharField(max_length=50, default='')

    def __str__(self):
        return self._get_name()

    def _get_name(self):
        name = os.path.basename(self.entry_name)
        return name


class GraphEntries(models.Model):

    entry_path = models.CharField(max_length=500, default='')
    entry_id = models.CharField(max_length=500, default='')
    entry_name = models.CharField(max_length=500, default='')
    entry_version = models.CharField(max_length=500, default='')

    def __str__(self):
        return self._get_id()

    def _get_id(self):
        return self.entry_id+"_"+self.entry_version


class SubmittedCatelogueEntries(models.Model):
    docfile = models.FileField(upload_to='submitted/%Y/%m/%d')
    username = models.CharField(max_length=200, default='')
    user_email = models.CharField(max_length=200, default='')
    STATUS_CHOICES = [
        ('i', 'In process'),
        ('a', 'Accepted'),
        ('r', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='i'
    )

    def set_uploader(self, name, email):
        self.username = name
        self.user_email = email

    def confirm(self):
        self.status = 'accepted'

    def reject(self):
        self.status = 'rejected'

    def __str__(self):
        return self._get_name()

    def _get_name(self):
        return self.docfile.name

    def unzip_files(self):
        if tarfile.is_tarfile(self.docfile.path):
            with tarfile.TarFile(self.docfile.path, 'r') as tar_ref:
                tar_ref.extractall(str(settings.TEMP_DIR)+'/'+self.docfile.name+'/')

        elif zipfile.is_zipfile(self.docfile.path):
            with zipfile.ZipFile(self.docfile.path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(settings.TEMP_DIR))
