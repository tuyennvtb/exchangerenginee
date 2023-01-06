from django.db import models

# Create your models here.
class Logger_Incoming_Request(models.Model):
    ID = models.AutoField(primary_key=True)
    url =  models.CharField(max_length=100, null=False)
    payload =  models.TextField()
    response =  models.TextField()  
    timestamp = models.DateTimeField(null=True)  

    class Meta:
        db_table = "logger_incoming_request"

class Logger_Outgoing_Request(models.Model):
    ID = models.AutoField(primary_key=True)
    url =  models.CharField(max_length=100, null=False)
    payload =  models.TextField()
    response =  models.TextField()
    timestamp = models.DateTimeField(null=True)


    class Meta:
        db_table = "logger_outcoming_request"


class Logger_Transaction(models.Model):
    ID = models.AutoField(primary_key=True)
    transaction_id =  models.CharField(max_length=100, null=False)
    description = models.TextField()
    timestamp = models.DateTimeField(null=True)

    class Meta:
        db_table = "logger_transaction"

class Logger_Broker(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id =  models.CharField(max_length=100, null=False)
    message = models.TextField()
    timestamp = models.DateTimeField(null=True)

    class Meta:
        db_table = "logger_broker"