from rest_framework import serializers
from .models import Usuario, Tarefa, Cliente
from bson import ObjectId
from datetime import datetime

class UsuarioSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'tipo', 'status']
    
    def get_id(self, obj):
        return str(obj._id)

class UsuarioLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        senha = attrs.get('senha')
        
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.check_password(senha):
                attrs['usuario'] = usuario
                return attrs
            else:
                raise serializers.ValidationError('Email ou senha incorretos.')
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Email ou senha incorretos.')

class UsuarioRegistrationSerializer(serializers.ModelSerializer):
    senha_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'senha_confirm']
        extra_kwargs = {'senha': {'write_only': True}}
    
    def validate(self, attrs):
        if attrs['senha'] != attrs['senha_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('senha_confirm')
        usuario = Usuario(**validated_data)
        usuario.set_password(validated_data['senha'])
        usuario.save()
        return usuario

class TarefaSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    idUsuario = serializers.SerializerMethodField()
    is_completed = serializers.ReadOnlyField()
    prioridade_texto = serializers.ReadOnlyField()
    usuario_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarefa
        fields = [
            'id', 'idUsuario', 'titulo', 'descricao', 'status', 
            'prioridade', 'prioridade_texto', 'data_inicio', 'data_termino',
            'is_completed', 'usuario_nome', 'idCampanha'
        ]
    
    def get_id(self, obj):
        return str(obj._id)
    
    def get_idUsuario(self, obj):
        return str(obj.idUsuario)
    
    def get_usuario_nome(self, obj):
        try:
            usuario = Usuario.objects.get(_id=obj.idUsuario)
            return usuario.nome
        except Usuario.DoesNotExist:
            return "Usuário não encontrado"
    
    def create(self, validated_data):
        # Converter string de usuário para ObjectId se necessário
        if 'usuario' in self.context:
            validated_data['idUsuario'] = self.context['usuario']._id
        return super().create(validated_data)

class ClienteSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'razao_social', 'nome', 'telefone', 'celular', 'email',
            'cidade', 'empresa', 'cpf_cnpj', 'RG', 'data_nascimento',
            'endereco', 'observacoes', 'vendedor'
        ]
    
    def get_id(self, obj):
        return str(obj._id)