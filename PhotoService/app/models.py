from django.db import models

# Create your models here.

class Photo(models.Model):
    title = models.CharField(max_length=150)
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos') #ImageFieldを使うにはPillowというパッケージが必要
    created_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return self.title
     