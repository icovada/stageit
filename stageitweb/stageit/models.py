from django.db import models

# Create your models here.
class Templates(models.Model):
    """Defines templates table."""
    description = models.TextField(max_length=50)
    filepath = models.TextField(max_length=256)
    installmode = models.TextField(max_length=20)
    name = models.TextField(max_length=50, unique=True, null=False)
    platform = models.TextField(max_length=30, null=False)
    poststaging = models.TextField
    template = models.TextField
    templatevalues = models.BinaryField
    tasks = models.ForeignKey(Tasks, on_delete=models.CASCADE)