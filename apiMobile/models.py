from django.db import models

# Create your models here.
class rawComplaints(models.Model):

    nim = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    tanggal = models.DateField(auto_now_add=True)
    keluhan = models.TextField()

    class Meta:
        db_table = 'tb_raw_complaint'

    def __str__(self):
        return self.keluhan

#Model Kategori
class Kategori(models.Model):
    kategori = models.CharField(max_length=200)

    class Meta:
        db_table = 'tb_kategori'
    
    def __str__(self):
        return self.kategori

#Model Status
class Status(models.Model):
    status = models.CharField(max_length=150)

    class Meta:
        db_table = 'tb_status'

    def __str__(self):
        return self.status

def upload_path(instance, filename):
    return '/'.join(['images', 'complaint', filename])

#Images Model
class ImagesModel(models.Model):
    path = models.ImageField(blank=True, null=True, upload_to=upload_path)
    img_name = models.CharField(max_length=150, null=True, blank=True, default="img")

    class Meta:
        db_table = 'tb_images'

    def __str__(self):
        return self.img_name

#Model Complaint
class Complaint(models.Model):

    STATUS_SENTIMEN = (('Negatif', 'Negatif'),
            ('Positif', 'Positif')
    )
    keluhan = models.TextField()
    nim = models.CharField(max_length=20, default='000000')
    email = models.EmailField(max_length=100, default='user@email.com')
    sentimen = models.CharField(max_length=100, choices=STATUS_SENTIMEN)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name='complaint')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='complaint')
    tanggapan = models.TextField(null=True, blank=True)
    tanggal = models.DateField(auto_now_add=True)
    image = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tb_complaint'
    
    def __str__(self):
        return self.keluhan

#Model Admin
class Admin(models.Model):
    STATUS_ADMIN = (('Super Admin', 'Super Admin'),
                    ('Admin', 'Admin')
                )
    username = models.CharField(max_length=200, unique=True)
    nama = models.CharField(max_length=150)
    nik = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=200)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name='admin')
    status_admin = models.CharField(max_length=100, choices=STATUS_ADMIN)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'tb_admin'

    def __str__(self):
        return self.username

#Model Token
class Token(models.Model):
    token = models.TextField(null=True, blank=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin')

    class Meta:
        db_table = 'tb_token'

    def __str__(self):
        return self.token