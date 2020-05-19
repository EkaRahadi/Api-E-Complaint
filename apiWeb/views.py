from django.shortcuts import render
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .serializers import RawComplaintSerializer

# Create your views here.

@csrf_exempt
@api_view(['POST'])
def rawComplaint(request):
    serializer = RawComplaintSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data})
    else:
        return Response({'success': False, 'message': 'something wrong'}, status=400)