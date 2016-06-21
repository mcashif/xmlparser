from django.db import models

# Create your models here.

class XMLFile(models.Model):
    file_name = models.CharField(max_length=200,null=True)
    file_data = models.FileField(upload_to='dbdata')
    dump_url = models.URLField(max_length=200, blank=True)


class XMLData(models.Model):
    nodeID  = models.BigIntegerField(primary_key=True)
    nodeName = models.CharField(max_length=200,null=True)
    nodeparentName = models.CharField(max_length=200,null=True)
    nodeparentID = models.IntegerField(default=0)
    nodeattribute = models.CharField(max_length=520,null=True)
    nodedata = models.CharField(max_length=10024,null=True)
    linktoparent = models.CharField(max_length=5024,null=True)
