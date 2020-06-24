from rest_framework import serializers
from .models import Admin, Kategori, Complaint, Status, rawComplaints
from django.contrib.auth.hashers import make_password


class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id','kategori']


class AdminSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer()
    class Meta:
        model = Admin
        fields = ['id','username','nama','nik','jabatan','kategori','status_admin','token', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
    
    def create(self, validated_data):
        kategori_id = validated_data['kategori']
        print(kategori_id['kategori'])
        admin = Admin.objects.create(username=validated_data['username'],
                                    nama=validated_data['nama'],
                                    nik=validated_data['nik'],
                                    jabatan=validated_data['jabatan'],
                                    status_admin=validated_data['status_admin'],
                                    password=make_password(validated_data['password']),
                                    kategori=Kategori.objects.get(id=kategori_id['kategori']),
                                    token=validated_data['token']
                                     )
        return admin
    
    def update(self, instance, validated_data):
        print(validated_data['kategori'])
        kategori_id = validated_data['kategori']

        instance.kategori = Kategori.objects.get(id=kategori_id['kategori'])
        instance.username = validated_data.get('username', instance.username)
        instance.nama = validated_data.get('nama', instance.nama)
        instance.nik = validated_data.get('nik', instance.nik)
        instance.jabatan = validated_data.get('jabatan', instance.jabatan)
        instance.status_admin = validated_data.get('status_admin', instance.status_admin)
        instance.password = make_password(validated_data['password'])
        instance.token = validated_data.get('token', instance.token)

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
        fields = ['id','keluhan', 'sentimen', 'kategori', 'status','tanggapan', 'tanggal']
    
    def create(self, validated_data):

        status_id = validated_data['status']
        kategori_data = validated_data['kategori']
        complaint = Complaint.objects.create(keluhan=validated_data['keluhan'],
                                            sentimen=validated_data['sentimen'],
                                            kategori=Kategori.objects.get(kategori__iexact=kategori_data['kategori']),
                                            status = Status.objects.get(id=status_id['status'])
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
        fields = ['id','username','nama','nik','jabatan','kategori','status_admin','token', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
