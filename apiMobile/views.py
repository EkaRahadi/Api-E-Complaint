from django.shortcuts import render
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .serializers import AdminSerializer, ComplaintSerializer, StatusSerializer, KategoriSerializer, AdminPartialSerializer
from .models import Admin, Complaint, Status, Kategori
from onesignal import OneSignal, DeviceNotification
from django.conf import settings
#Import sent_tokenize untuk splitting text ke per kalimat
from nltk.tokenize import sent_tokenize

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
        serializer = AdminSerializer(admin)

        return Response({'success': True, 'data': serializer.data})
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
            super_admin = Admin.objects.filter(status_admin="Super Admin").exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True).order_by('id')
            try:
                status_id = request.data['status']
                status = Status.objects.get(id=status_id['status'])
                if status.status=='Pending':
                    serializer = ComplaintSerializer(complaint, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        if len(super_admin) > 0 :
                            '''Sent Notif to Super Admin Here   '''
                            notification_to_users = DeviceNotification(
                                contents={
                                    "en": "Buka untuk beri tinjauan"
                                },
                                headings={
                                    "en": "Ada Laporan"
                                },
                                include_player_ids=list(super_admin),
                                include_external_user_ids = list(super_admin)
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
    keluhan = sent_tokenize(keluhan_raw)
    sentimen = model_sentimen.predict(keluhan)
    kategori = model_kategori.predict(keluhan)
    #Insert DB

    for index in range(len(keluhan)):
        keluhan_input = {
            'keluhan' : keluhan[index],
            'sentimen' : sentimen[index],
            'kategori' : {
                'kategori': kategori[index]
            },
            'status' : {
                'status' : 1
            }
        }
        kategoriId = list(Kategori.objects.filter(kategori__iexact = kategori[index]).values_list('id', flat=True))[0]
        print(kategoriId)
        admin = Admin.objects.filter(status_admin="Admin", kategori = kategoriId).exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True).order_by('id')
        if len(admin) > 0 :
            notification_to_users = DeviceNotification(
                contents={
                    "en": "Buka untuk memberi tanggapan"
                },
                headings={
                    "en": "Keluhan Baru"
                },
                include_player_ids=list(admin),
                include_external_user_ids = list(admin)
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

# @csrf_exempt
# @api_view(['GET'])
# def testNotif(request):
#     #onesignal instance
#     admin = Admin.objects.filter(status_admin="Admin", kategori=2).exclude(token__isnull=True).exclude(token__exact='').values_list('token', flat=True).order_by('id')
#     admin = list(admin)
#     admin1 = Admin.objects.filter(status_admin="Admin", kategori=2).values_list('token', flat=True).order_by('id')
#     notification_to_users = DeviceNotification(
#         contents={
#             "en": "Buka untuk beri tinjauan"
#         },
#         headings={
#             "en": "Ada Laporan"
#         },
#         include_player_ids=list(admin),
#         include_external_user_ids = list(admin)
#     )
#     client.send(notification_to_users)
#     print(admin)
#     print(list(admin1))
#     # kategoriId = list(Kategori.objects.filter(kategori__iexact = 'KEUANGAN').values_list('id', flat=True))[0]
#     # print(kategoriId)
#     return Response({'success': True, 'message': 'Notifikasi terkirim'})

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