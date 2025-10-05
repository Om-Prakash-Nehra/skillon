import json
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Ticket, Comment, Timeline
from .serializers import RegisterSerializer, TicketSerializer, CommentSerializer
from django.views.generic import TemplateView

# Rate limit
class SixtyPerMinute(UserRateThrottle):
    rate = '60/min'

def standard_error(detail, code=400):
    return Response({'error': {'message': str(detail), 'code': code}}, status=code)

# ----------------- Auth -----------------
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SixtyPerMinute])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = serializer.data
        data.update({'access': str(refresh.access_token)})
        return Response(data, status=status.HTTP_201_CREATED)
    return standard_error(serializer.errors, 400)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SixtyPerMinute])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {'username': user.username, 'role': user.role, 'is_superuser': user.is_superuser}
        })
    return standard_error('Invalid credentials', 401)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({'username': user.username, 'email': user.email, 'role': user.role, 'is_superuser': user.is_superuser})

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status':'ok'})

# ----------------- Tickets -----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SixtyPerMinute])
def ticket_list(request):
    user = request.user
    qs = Ticket.objects.all()
    if user.role == 'user':
        qs = qs.filter(created_by=user)
    elif user.role == 'agent':
        qs = qs.filter(assigned_to=user)
    search = request.GET.get('search')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(comments__content__icontains=search)).distinct()
    limit = int(request.GET.get('limit',10))
    offset = int(request.GET.get('offset',0))
    serializer = TicketSerializer(qs[offset:offset+limit], many=True)
    return Response({'count': qs.count(), 'limit': limit, 'offset': offset, 'results': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SixtyPerMinute])
def ticket_create(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            ticket = serializer.save(created_by=request.user)
            Timeline.objects.create(ticket=ticket, action="Ticket created", user=request.user)
            return Response(TicketSerializer(ticket).data, status=201)
    return standard_error(serializer.errors, 400)

@api_view(['GET','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([SixtyPerMinute])
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    if request.method == 'GET':
        if user.role == 'user' and ticket.created_by != user:
            return standard_error('Forbidden', 403)
        if user.role == 'agent' and ticket.assigned_to != user:
            return standard_error('Forbidden', 403)
        return Response(TicketSerializer(ticket).data)
    
    if request.method == 'PATCH':
        allowed = {}
        if user.is_superuser:
            allowed = request.data
        elif user.role == 'user' and ticket.created_by == user:
            for k in ['title','description','priority','sla_hours']:
                if k in request.data:
                    allowed[k] = request.data[k]
        elif user.role == 'agent' and ticket.assigned_to == user:
            if 'status' in request.data:
                allowed['status'] = request.data['status']
        serializer = TicketSerializer(ticket, data=allowed, partial=True)
        if serializer.is_valid():
            ticket.version += 1
            serializer.save(version=ticket.version)
            Timeline.objects.create(ticket=ticket, action="Ticket updated", user=user)
            return Response(serializer.data)
        return standard_error(serializer.errors,400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SixtyPerMinute])
def comment_create(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    if user.role == 'user' and ticket.created_by != user:
        return standard_error('Forbidden',403)
    if user.role == 'agent' and ticket.assigned_to != user:
        return standard_error('Forbidden',403)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            comment = serializer.save(user=user, ticket=ticket)
            Timeline.objects.create(ticket=ticket, action="Comment added", user=user)
            return Response(CommentSerializer(comment).data, status=201)
    return standard_error(serializer.errors,400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SixtyPerMinute])
def assign_ticket(request, pk):
    if not request.user.is_superuser:
        return standard_error('Forbidden',403)
    ticket = get_object_or_404(Ticket, pk=pk)
    agent_id = request.data.get('agent_id')
    agent = get_object_or_404(User, pk=agent_id, role='agent')
    ticket.assigned_to = agent
    ticket.status = 'assigned'
    ticket.version += 1
    ticket.save()
    Timeline.objects.create(ticket=ticket, action=f"Assigned to {agent.username}", user=request.user)
    return Response({'detail':'Ticket assigned','assigned_to':agent.username})

class RegisterPageView(TemplateView):
    template_name = "tickets/register.html"

class LoginPageView(TemplateView):
    template_name = "tickets/index.html"