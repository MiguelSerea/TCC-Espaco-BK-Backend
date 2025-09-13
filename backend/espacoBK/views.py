from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .models import Usuario, Tarefa, Cliente
from .serializers import (
    UsuarioSerializer, UsuarioLoginSerializer, UsuarioRegistrationSerializer,
    TarefaSerializer, ClienteSerializer
)
from bson import ObjectId
from datetime import datetime

# Função para autenticação customizada
def get_usuario_from_token(request):
    """Busca usuário baseado no token customizado"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        # Implementar lógica de token customizada ou usar sessão
        # Por enquanto, vamos usar uma abordagem simples
        try:
            # Você pode implementar sua própria lógica de token aqui
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                return Usuario.objects.get(_id=ObjectId(usuario_id))
        except:
            pass
    return None

# ==================== AUTENTICAÇÃO ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registra um novo usuário"""
    serializer = UsuarioRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        return Response({
            'success': True,
            'message': 'Usuário criado com sucesso!',
            'user': UsuarioSerializer(usuario).data,
            'token': str(usuario._id)  # Token simples usando ID
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Erro ao criar usuário',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Realiza login do usuário"""
    serializer = UsuarioLoginSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.validated_data['usuario']
        
        # Salvar na sessão
        request.session['usuario_id'] = str(usuario._id)
        
        return Response({
            'success': True,
            'message': 'Login realizado com sucesso!',
            'user': UsuarioSerializer(usuario).data,
            'token': str(usuario._id)
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Erro ao fazer login',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_user(request):
    """Realiza logout do usuário"""
    try:
        request.session.flush()
        return Response({
            'success': True,
            'message': 'Logout realizado com sucesso!'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erro ao fazer logout',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def check_auth(request):
    """Verifica se o usuário está autenticado"""
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
            return Response({
                'success': True,
                'authenticated': True,
                'user': UsuarioSerializer(usuario).data
            }, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            pass
    
    return Response({
        'success': False,
        'authenticated': False
    }, status=status.HTTP_401_UNAUTHORIZED)

# ==================== TAREFAS ====================

@api_view(['GET', 'POST'])
def tarefas_list(request):
    """Lista tarefas ou cria nova tarefa"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return Response({'success': False, 'message': 'Não autenticado'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(idUsuario=ObjectId(usuario_id))
        serializer = TarefaSerializer(tarefas, many=True)
        return Response({
            'success': True,
            'tarefas': serializer.data,
            'total': tarefas.count()
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = TarefaSerializer(data=request.data)
        if serializer.is_valid():
            # Adicionar ID do usuário
            tarefa = serializer.save(idUsuario=ObjectId(usuario_id))
            return Response({
                'success': True,
                'message': 'Tarefa criada com sucesso!',
                'tarefa': TarefaSerializer(tarefa).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erro ao criar tarefa',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def tarefa_detail(request, pk):
    """Operações em tarefa específica"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return Response({'success': False, 'message': 'Não autenticado'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        tarefa = Tarefa.objects.get(_id=ObjectId(pk), idUsuario=ObjectId(usuario_id))
    except Tarefa.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarefa não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TarefaSerializer(tarefa)
        return Response({
            'success': True,
            'tarefa': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = TarefaSerializer(tarefa, data=request.data, partial=True)
        if serializer.is_valid():
            tarefa_atualizada = serializer.save()
            return Response({
                'success': True,
                'message': 'Tarefa atualizada com sucesso!',
                'tarefa': TarefaSerializer(tarefa_atualizada).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Erro ao atualizar tarefa',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        tarefa.delete()
        return Response({
            'success': True,
            'message': 'Tarefa excluída com sucesso!'
        }, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def marcar_tarefa_concluida(request, pk):
    """Marca/desmarca tarefa como concluída"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return Response({'success': False, 'message': 'Não autenticado'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        tarefa = Tarefa.objects.get(_id=ObjectId(pk), idUsuario=ObjectId(usuario_id))
        
        # Alternar status: 1=pendente, 2=concluída
        tarefa.status = "2" if tarefa.status == "1" else "1"
        tarefa.save()
        
        status_texto = 'concluída' if tarefa.status == "2" else 'pendente'
        
        return Response({
            'success': True,
            'message': f'Tarefa marcada como {status_texto}!',
            'tarefa': TarefaSerializer(tarefa).data
        }, status=status.HTTP_200_OK)
        
    except Tarefa.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarefa não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

# ==================== CLIENTES ====================

@api_view(['GET', 'POST'])
def clientes_list(request):
    """Lista clientes ou cria novo cliente"""
    if request.method == 'GET':
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response({
            'success': True,
            'clientes': serializer.data,
            'total': clientes.count()
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            return Response({
                'success': True,
                'message': 'Cliente criado com sucesso!',
                'cliente': ClienteSerializer(cliente).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erro ao criar cliente',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)