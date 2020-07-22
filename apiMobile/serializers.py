from rest_framework import serializers
from .models import Admin, Kategori, Complaint, Status, Token, ImagesModel
from django.contrib.auth.hashers import make_password


class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id','kategori']


class AdminSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer()
    class Meta:
        model = Admin
        fields = ['id','username','nama','nik','jabatan','kategori','status_admin', 'password', 'jurusan']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
    
    def create(self, validated_data):
        kategori_id = validated_data['kategori']
        print(kategori_id['kategori'])
        admin = Admin.objects.create(username=validated_data['username'],
                                    nama=validated_data['nama'],
                                    nik=validated_data['nik'],
                                    jurusan=validated_data['jurusan'],
                                    jabatan=validated_data['jabatan'],
                                    status_admin=validated_data['status_admin'],
                                    password=make_password(validated_data['password']),
                                    kategori=Kategori.objects.get(id=kategori_id['kategori'])
                                     )
        return admin
    
    def update(self, instance, validated_data):
        print(validated_data['kategori'])
        kategori_id = validated_data['kategori']

        instance.kategori = Kategori.objects.get(id=kategori_id['kategori'])
        instance.username = validated_data.get('username', instance.username)
        instance.nama = validated_data.get('nama', instance.nama)
        instance.jurusan = validated_data.get('jurusan', instance.jurusan)
        instance.nik = validated_data.get('nik', instance.nik)
        instance.jabatan = validated_data.get('jabatan', instance.jabatan)
        instance.status_admin = validated_data.get('status_admin', instance.status_admin)
        instance.password = make_password(validated_data['password'])

        instance.save()
        return instance

#Status Serializer
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id','status']

#ComplaintSerializer
class ComplaintSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer()
    status = StatusSerializer()

    class Meta:
        model = Complaint
        fields = ['id','keluhan', 'nim', 'email','sentimen', 'kategori', 'status','tanggapan', 'tanggal', 'image', 'jurusan']
    
    def create(self, validated_data):

        status_id = validated_data['status']
        kategori_data = validated_data['kategori']
        complaint = Complaint.objects.create(keluhan=validated_data['keluhan'],
                                            sentimen=validated_data['sentimen'],
                                            jurusan = validated_data['jurusan'],
                                            nim=validated_data['nim'],
                                            email=validated_data['email'],
                                            kategori=Kategori.objects.get(kategori__iexact=kategori_data['kategori']),
                                            status = Status.objects.get(id=status_id['status']),
                                            image = validated_data['image']
                                     )
        return complaint
    
    def update(self, instance, validated_data):
        status_id = validated_data['status']
        instance.status = Status.objects.get(id=status_id['status'])
        instance.tanggapan = validated_data['tanggapan']

        instance.save()
        return instance

#Admin Partial Update
class AdminPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id','username','nama','nik','jabatan','kategori','status_admin','password', 'jurusan']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesModel
        fields = '__all__'