from django.shortcuts import render
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .serializers import AdminSerializer, ComplaintSerializer, StatusSerializer, KategoriSerializer, AdminPartialSerializer, TokenSerializer, ImagesSerializer
from .models import Admin, Complaint, Status, Kategori, Token, ImagesModel
from onesignal import OneSignal, DeviceNotification
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
#Import sent_tokenize untuk splitting text ke per kalimat
from nltk.tokenize import sent_tokenize

# Library RegEx
import re

#Import for PDF
from django.shortcuts import render
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from django.http import HttpResponse

# Create your views here.
model_sentimen = getattr(settings, 'MODEL_SENTIMEN', 'Gak iso diload')
model_kategori = getattr(settings, 'MODEL_KATEGORI', 'Gak iso diload')

client = OneSignal("85ef8ba5-0492-42a1-aa5c-b8f17e434621", 
                "NjQwOGNjODgtYTA2Mi00OGZmLTlkYjktZTc1ODEzOTRiMmI2")

@csrf_exempt
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Login':'/login/',
        'AdminList': '/admin/',
        'CreateAdmin': '/admin/',
        'UpdateAdmin': '/admin/<int:pk>/',
        'DeleteAdmin': '/admin/<int:pk>/',
        'UpdateTokenFirebase': '/admin/<int:pk>/',
        'ComplaintList': '/complaints/',
        'ComplaintListByCategory': '/complaints/<int:pk>/',
        'UpdateStatusComplaint': '/complaint/'
    }
    return Response(api_urls)

@api_view(['GET'])
def banyakCompalint(request):
    keluhan = Complaint.objects.all()
    akademik = 0
    pengajar = 0
    sarpras = 0
    keuangan = 0

    for k in keluhan:
        if str(k.kategori) == 'Keuangan':
            keuangan += 1
        elif str(k.kategori) == 'Sarana Prasarana':
            sarpras += 1
        elif str(k.kategori) == 'Tenaga Pengajar (Dosen)':
            pengajar += 1
        elif str(k.kategori) == 'Akademik':
            akademik += 1
    
    return Response({'success': True, 'data': [
        {'nama': 'Akademik','jumlah': akademik},
        {'nama': 'Tenaga Pengajar','jumlah': pengajar},
        {'nama': 'Sarana Prasarana','jumlah': sarpras},
        {'nama': 'Keuangan','jumlah': keuangan}
    ]})

@csrf_exempt
@api_view(['POST'])
def loginAdmin(request):
    data = request.data
    username = data['username']
    password = data['password']

    try:
        admin = Admin.objects.get(username=username)
        password_check = check_password(password, admin.password)
        if password_check == True:
            serializer = AdminSerializer(admin)
            return Response({'success': True, 'data': serializer.data})
        else:
            return Response({'success': False, 'data': []}, status=404)
    except:
        return Response({'success': False, 'data': []}, status=404)

@csrf_exempt
@api_view(['GET', 'POST'])
def adminListCreate(request):

    if request.method=='GET':
        admin = Admin.objects.all()
        serializers = AdminSerializer(admin, many=True)
        if len(admin) > 0:
            return Response({'success': True, 'data': serializers.data})
        else:
            return Response({'success': False, 'data': []}, status=404)
    else:
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=201)
        elif serializer.is_valid() == False:
            return Response({'success': False, 'data': serializer.errors}, status=400)

@csrf_exempt
@api_view(['POST', 'DELETE'])
def updateDeleteAdmin(request, pk):
    if request.method == 'POST':
        try:
            admin = Admin.objects.get(id=pk)
            serializer = AdminSerializer(admin, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'data': serializer.data})
            elif serializer.is_valid() == False:
                return Response({'success': False, 'data': serializer.errors}, status=400)
        except Admin.DoesNotExist:
            return Response({'success': False, 'message': 'user tidak ditemukan'})
    else:
        try:
            admin = Admin.objects.get(id=pk)
            admin.delete()

            return Response({'success': True, 'message': 'user berhasil didelete'})
        except Admin.DoesNotExist:
            return Response({'success': False, 'message': 'user tidak ditemukan'})

@csrf_exempt
@api_view(['GET', 'POST'])
def listUpdateComplaint(request):

    if request.method == 'POST':
        try:
            complaint = Complaint.objects.get(id=request.data['id'])
            # super_admin = Admin.objects.filter(status_admin="Super Admin").exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True).order_by('id')
            super_admin_list = Admin.objects.filter(status_admin="Super Admin")
            token_list = []
            for admin in super_admin_list:
                token = Token.objects.filter(admin=admin.id).exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True)
                token_list += token
            print(token_list)
            try:
                status_id = request.data['status']
                status = Status.objects.get(id=status_id['status'])
                if status.status=='Pending':
                    serializer = ComplaintSerializer(complaint, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        if len(token_list) > 0 :
                            '''Sent Notif to Super Admin Here   '''
                            notification_to_users = DeviceNotification(
                                contents={
                                    #"en": "Buka untuk beri tinjauan"
                                    "en": str(complaint.keluhan)
                                },
                                headings={
                                    "en": "Ada Laporan"
                                },
                                include_player_ids=token_list,
                                include_external_user_ids = token_list
                            )
                            client.send(notification_to_users)
                            print("Notif Firebase")
                        return Response({'success': True, 'data': serializer.data})
                    elif serializer.is_valid() == False:
                        return Response({'success': False, 'data': serializer.errors}, status=400)
                else :
                    serializer = ComplaintSerializer(complaint, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'success': True, 'data': serializer.data})
                    elif serializer.is_valid() == False:
                        return Response({'success': False, 'data': serializer.errors}, status=400)

            except Status.DoesNotExist:
                return Response({'success': False, 'message': 'id status salah'})
        except Complaint.DoesNotExist:
            return Response({'success': False, 'message':'id complaint tidak ditemukan'})
    else:
        complaint = Complaint.objects.all()
        if len(complaint) > 0:
            serializer = ComplaintSerializer(complaint, many=True)
            return Response({'success': True, 'data': serializer.data})
        else:
            return Response({'success': False, 'data':[]}, status=404)

@csrf_exempt
@api_view(['GET', 'POST'])
def listComplaintCategory(request, pk):
    if request.method == 'GET':
        complaint = Complaint.objects.filter(kategori=pk)
    else:
        if int(pk) == 4:
            if request.data.get("jurusan", None) == None:
                date = request.data['date']
                month = date[0:2]
                year = date[3:7]
                complaint = Complaint.objects.filter(kategori=pk,
                                tanggal__year=year, 
                                tanggal__month=month)
            else:
                jurusan = request.data['jurusan']
                complaint = Complaint.objects.filter(kategori=pk, jurusan__iexact=jurusan)
        else:
            if len(request.data) > 0:
                date = request.data['date']
                month = date[0:2]
                year = date[3:7]
                complaint = Complaint.objects.filter(kategori=pk,
                                tanggal__year=year, 
                                tanggal__month=month)
            else:
                complaint = Complaint.objects.filter(kategori=pk)

    if len(complaint) > 0 :
        serializer = ComplaintSerializer(complaint, many=True)
        return Response({'success': True, 'data': serializer.data})
    else:
        return Response({'success': False, 'data': []}, status=404)

@csrf_exempt
@api_view(['GET'])
def listCategory(request):
    kategori = Kategori.objects.all()
    serializer = KategoriSerializer(kategori, many=True)

    if len(kategori) > 0:
        return Response({'success': True, 'data': serializer.data})
    else:
        return Response({'success': False, 'data':[]}, status=404)

@csrf_exempt
@api_view(['GET'])
def listStatus(request):
    status = Status.objects.all()
    serializer = StatusSerializer(status, many=True)

    if len(status) > 0:
        return Response({'success': True, 'data': serializer.data})
    else:
        return Response({'success': False, 'data': []}, status=404)

@csrf_exempt
@api_view(['POST'])
def complaintCreate(request):
    serializer = []
    #Analaysis
    keluhan_raw = request.data['keluhan']
    data_kotor = re.findall(r'(?:\d[,.]|[^,.])*(?:[,.]|$)', keluhan_raw)
    data_kotor.remove('')
    data_bersih = []

    for text in data_kotor:
        data_bersih = data_bersih + text.split("dan")
    
    #Inser Gambar ke tabel Gambar
    path_img = None
    if request.FILES.get("path", None) != None:
        print("Ada Gambar")
        img_name = request.FILES["path"].name
        data_image = {
            "path": request.data["path"],
            "img_name": img_name
        }
        serializer_image = ImagesSerializer(data=data_image)
        if serializer_image.is_valid():
            serializer_image.save()
        path_img = serializer_image.data.get("path")
    else:
        print("Tidak ada Gambar")
    # Prediksi
    sentimen = model_sentimen.predict(data_bersih)
    kategori = model_kategori.predict(data_bersih)

    #Insert DB
    for index in range(len(data_bersih)):
        if path_img == None:
            keluhan_input = {
            'keluhan' : data_bersih[index],
            'nim': request.data['nim'],
            'email': request.data['email'],
            'sentimen' : sentimen[index],
            'jurusan': request.data['jurusan'],
            'kategori' : {
                'kategori': kategori[index]
            },
            'status' : {
                'status' : 1
            },
            'image': None
        }
        else:
            keluhan_input = {
            'keluhan' : data_bersih[index],
            'nim': request.data['nim'],
            'email': request.data['email'],
            'sentimen' : sentimen[index],
            'jurusan': request.data['jurusan'],
            'kategori' : {
                'kategori': kategori[index]
            },
            'status' : {
                'status' : 1
            },
            'image' : path_img
        }

        kategoriId = list(Kategori.objects.filter(kategori__iexact = kategori[index]).values_list('id', flat=True))[0]
        admin_list = Admin.objects.filter(status_admin="Admin", kategori = kategoriId)
        token_list = []
        for admin in admin_list:
            token = Token.objects.filter(admin=admin.id).exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True)
            token_list += token
        print(token_list)

        if len(token_list) > 0 :
            notification_to_users = DeviceNotification(
                contents={
                    #"en": "Buka untuk memberi tanggapan"
                    "en": str(data_bersih[index])
                },
                headings={
                    "en": "Keluhan Baru"
                },
                include_player_ids=token_list,
                include_external_user_ids = token_list
            )
            client.send(notification_to_users)

        serializer.append(ComplaintSerializer(data=keluhan_input))
        if serializer[index].is_valid():
            serializer[index].save()
        else:
            return Response({'success': False, 'message': serializer[index].errors})
    
    return Response({'success': True, 'message': 'complaint dimasukkan'})

@csrf_exempt
@api_view(['POST'])
def tokenPartialUpdate(request, pk):
    try:
        admin = Admin.objects.get(id=pk)
        serializer = AdminPartialSerializer(admin, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        elif serializer.is_valid() == False:
            return Response({'success': False, 'data': serializer.errors}, status=400)
    except Admin.DoesNotExist:
        return Response({'success': False, 'message': 'user tidak ditemukan'})

@csrf_exempt
@api_view(['GET'])
def listComplaintStatus(request, pk):
    try:
        complaint_pending = Complaint.objects.filter(status=pk)
        if len(complaint_pending) > 0 :
            serializer = ComplaintSerializer(complaint_pending, many=True)
            return Response({'success': True, 'data': serializer.data})
        else:
            return Response({'success': False, 'data': []}, status=404)
    except Complaint.DoesNotExist:
        return Response({'success': False, 'message': 'Complaint tidak ditemukan'}, status=404)

@csrf_exempt
@api_view(['GET', 'POST'])
def listComplaintPdf(request, pk):
    if len(request.data) > 0:
        date = request.data['date']
        month = date[0:2]
        year = date[3:7]
        complaint = Complaint.objects.filter(kategori=pk,
                        tanggal__year=year, 
                        tanggal__month=month)
    else:
        complaint = Complaint.objects.filter(kategori=pk)

    data = {
        "complaint_list": complaint
    }
    pdf = render_to_pdf('pdf_template.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

#Fungsi merubah html to PDF
def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

#Token
@csrf_exempt
@api_view(['GET', 'POST'])
def token(request):
    admin_list = Admin.objects.filter(status_admin="Admin")
    token_list = []
    for admin in admin_list:
        token = Token.objects.filter(admin=admin.id).exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True)
        token_list += token
    print(type(token_list))
    if request.method == 'GET':
        token = Token.objects.all()
        serializer = TokenSerializer(token, many=True)
        return Response({'success': True, 'data': serializer.data})
    else:
        token = Token.objects.filter(token=request.data['token'])
        if len(token) > 0:
            serializer = TokenSerializer(token, many=True)
            return Response({'success': True, 'data': serializer.data})
        else:
            serializer = TokenSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'data': serializer.data})
            else:
                return Response({'success': False, 'data': []})

@csrf_exempt
@api_view(['DELETE'])
def deleteToken(request):
    try:
        token = Token.objects.get(token=request.data['token'])
        token.delete()

        return Response({'success': True, 'message': 'Token berhasil didelete'})
    except Token.DoesNotExist:
        return Response({'success': False, 'message': 'Token tidak ditemukan'})