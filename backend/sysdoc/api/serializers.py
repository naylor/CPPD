from rest_framework import serializers
from sysdoc import models
from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['userId'] = self.user.id
        data['is_staff'] = self.user.is_staff
        return data

# ---- NOVOS SERIALIZERS PARA PROCESSO ---- #
class ProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Processo
        fields = '__all__'

# ---- NOVOS SERIALIZERS PARA ITEMIZACAO ---- #
class ItemizacaoSerializer(serializers.ModelSerializer):
    processo_nome = serializers.CharField(source='processo.nome', read_only=True)
    itemSuperior_nome = serializers.CharField(source='itemSuperior.nome', read_only=True)

    class Meta:
        model = models.Itemizacao
        fields = ['id', 'nome', 'descricao', 'processo', 'processo_nome', 'ordem', 'itemSuperior', 'itemSuperior_nome']


    def get_subitemizacoes(self, obj):
        subitems = obj.subitems.all()
        return ItemizacaoSerializer(subitems, many=True).data

    def get_tarefas(self, obj):
        tarefas = models.TarefaProcesso.objects.filter(item=obj)
        return TarefaProcessoSerializer(tarefas, many=True).data

# ---- NOVOS SERIALIZERS PARA TAREFA-PROCESSO ---- #
class TarefaProcessoSerializer(serializers.ModelSerializer):
    processo_nome = serializers.CharField(source='processo.nome', read_only=True)
    item_nome = serializers.CharField(source='item.nome', read_only=True)

    class Meta:
        model = models.TarefaProcesso
        fields = ['id', 'nome', 'ponto', 'minimo', 'maximo', 'processo', 'descricao', 'processo_nome', 'item', 'item_nome']


class ItemizacaoTreeSerializer(serializers.ModelSerializer):
    subitemizacoes = serializers.SerializerMethodField()
    tarefas = serializers.SerializerMethodField()

    class Meta:
        model = models.Itemizacao
        fields = ['id', 'nome', 'descricao', 'ordem', 'itemSuperior', 'subitemizacoes', 'tarefas']

    def get_subitemizacoes(self, obj):
        queryset = models.Itemizacao.objects.filter(itemSuperior=obj).order_by('ordem')
        return ItemizacaoTreeSerializer(queryset, many=True).data

    def get_tarefas(self, obj):
        queryset = models.TarefaProcesso.objects.filter(item=obj)
        return TarefaProcessoSerializer(queryset, many=True).data

# ---- NOVOS SERIALIZERS PARA USUARIO-PROCESSO ---- #
class UsuarioProcessoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    usuario_nome = serializers.SerializerMethodField()
    processo = serializers.PrimaryKeyRelatedField(queryset=models.Processo.objects.all())
    processo_nome = serializers.CharField(source='processo.nome', read_only=True)
    processo_pontos = serializers.SerializerMethodField()  # ADICIONADO
    total_pontos = serializers.SerializerMethodField()
    link_processo_pdf = serializers.SerializerMethodField()
    log = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = models.UsuarioProcesso
        fields = [
            'id', 'usuario', 'usuario_nome', 'processo', 'status', 'data',
            'processo_nome', 'processo_pontos', 'total_pontos', 'link_processo_pdf', 'log'
        ]

    def get_usuario_nome(self, obj):
        full_name = obj.usuario.get_full_name()
        return full_name if full_name else obj.usuario.username

    def get_processo_pontos(self, obj):  # ADICIONADO
        return obj.processo.pontos if obj.processo and hasattr(obj.processo, "pontos") else 0

    def get_total_pontos(self, obj):
        docs = models.UsuarioDocs.objects.filter(usuarioProcesso=obj)
        total = 0
        for doc in docs:
            qde = doc.qdeReajustada if doc.qdeReajustada is not None else doc.quantidade
            ponto = doc.tarefaProcesso.ponto or 0
            total += (qde or 0) * ponto
        return total

    def get_link_processo_pdf(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                f'/gerar_pdf/{obj.processo.id}/{obj.usuario.id}/{obj.id}'
            )
        return None

# ---- NOVOS SERIALIZERS PARA USUARIO-DOCS ---- #
class UsuarioDocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UsuarioDocs
        fields = '__all__'
        extra_kwargs = {
            'tarefaProcesso': {'required': False},
            'usuarioProcesso': {'required': False},
            'file': {'required': False},
        }

    def update(self, instance, validated_data):
        instance.descricao = validated_data.get('descricao', instance.descricao)
        instance.quantidade = validated_data.get('quantidade', instance.quantidade)
        instance.qdeReajustada = validated_data.get('qdeReajustada', instance.qdeReajustada)
        instance.obsReajuste = validated_data.get('obsReajuste', instance.obsReajuste)

        if 'file' in validated_data:
            instance.file = validated_data.get('file', instance.file)

        instance.save()
        return instance

# ---- NOVOS SERIALIZERS PARA PROCESSO-TREE POR USUARIO ---- #
class UsuarioDocsMiniSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = models.UsuarioDocs
        fields = ['id', 'filename', 'quantidade', 'descricao', 'file', 'qdeReajustada', 'obsReajuste']

    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

class TarefaUsuarioSerializer(serializers.ModelSerializer):
    documentos = serializers.SerializerMethodField()
    total_pontos = serializers.SerializerMethodField()

    class Meta:
        model = models.TarefaProcesso
        fields = ['id', 'nome', 'ponto', 'minimo', 'maximo', 'descricao', 'documentos', 'total_pontos']

    def get_documentos(self, tarefa):
        usuario_processo = self.context['usuario_processo']
        request = self.context.get('request')
        docs = models.UsuarioDocs.objects.filter(
            tarefaProcesso=tarefa,
            usuarioProcesso=usuario_processo
        )
        return UsuarioDocsMiniSerializer(docs, many=True, context={'request': request}).data

    def get_total_pontos(self, tarefa):
        usuario_processo = self.context['usuario_processo']
        docs = models.UsuarioDocs.objects.filter(
            tarefaProcesso=tarefa,
            usuarioProcesso=usuario_processo
        )
        ponto = tarefa.ponto or 0
        total = sum([((doc.qdeReajustada if doc.qdeReajustada is not None else doc.quantidade) or 0) * ponto for doc in docs])
        return total

class ItemizacaoUsuarioSerializer(serializers.ModelSerializer):
    subitemizacoes = serializers.SerializerMethodField()
    tarefas = serializers.SerializerMethodField()
    total_pontos = serializers.SerializerMethodField()

    class Meta:
        model = models.Itemizacao
        fields = ['id', 'nome', 'descricao', 'subitemizacoes', 'tarefas', 'total_pontos']

    def get_subitemizacoes(self, obj):
        usuario_processo = self.context['usuario_processo']
        request = self.context.get('request')
        subs = obj.subitems.all()
        return ItemizacaoUsuarioSerializer(subs, many=True, context={'usuario_processo': usuario_processo, 'request': request}).data

    def get_tarefas(self, obj):
        usuario_processo = self.context['usuario_processo']
        request = self.context.get('request')
        tarefas = models.TarefaProcesso.objects.filter(item=obj)
        return TarefaUsuarioSerializer(tarefas, many=True, context={'usuario_processo': usuario_processo, 'request': request}).data

    def get_total_pontos(self, obj):
        usuario_processo = self.context['usuario_processo']
        tarefas = models.TarefaProcesso.objects.filter(item=obj)
        total_tarefas = sum([
            sum([((doc.qdeReajustada if doc.qdeReajustada is not None else doc.quantidade) or 0) * (tarefa.ponto or 0)
                 for doc in models.UsuarioDocs.objects.filter(tarefaProcesso=tarefa, usuarioProcesso=usuario_processo)])
            for tarefa in tarefas
        ])
        subs = obj.subitems.all()
        total_subs = sum([
            ItemizacaoUsuarioSerializer(sub, context={'usuario_processo': usuario_processo, 'request': self.context.get('request')}).get_total_pontos(sub)
            for sub in subs
        ])
        return total_tarefas + total_subs

class ProcessoTreeUsuarioSerializer(serializers.ModelSerializer):
    itemizacoes = serializers.SerializerMethodField()
    total_pontos = serializers.SerializerMethodField()
    link_processo_pdf = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.Processo
        fields = [
            'id', 'nome', 'inicio', 'fim', 'descricao', 'pontos', 'observacao',
            'itemizacoes', 'total_pontos', 'link_processo_pdf', 'status'
        ]

    def get_itemizacoes(self, obj):
        usuario_processo = self.context['usuario_processo']
        request = self.context.get('request')
        itemizacoes = models.Itemizacao.objects.filter(processo=obj, itemSuperior__isnull=True)
        return ItemizacaoUsuarioSerializer(itemizacoes, many=True, context={'usuario_processo': usuario_processo, 'request': request}).data

    def get_total_pontos(self, obj):
        usuario_processo = self.context['usuario_processo']
        itemizacoes = models.Itemizacao.objects.filter(processo=obj, itemSuperior__isnull=True)
        total = sum([
            ItemizacaoUsuarioSerializer(item, context={'usuario_processo': usuario_processo, 'request': self.context.get('request')}).get_total_pontos(item)
            for item in itemizacoes
        ])
        return total

    def get_link_processo_pdf(self, obj):
        usuario_processo = self.context.get('usuario_processo')
        request = self.context.get('request')
        if usuario_processo and request:
            url = request.build_absolute_uri(
                f'/gerar_pdf/{obj.id}/{usuario_processo.usuario.id}/{usuario_processo.id}'
            )
            return url
        return None

    def get_status(self, obj):
        usuario_processo = self.context.get('usuario_processo')
        return usuario_processo.status if usuario_processo else None

# ---- NOVOS SERIALIZERS PARA USUARIO ---- #
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email2 = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'email', 'email2', 'password')

    def validate(self, data):
        if data.get('email') != data.get('email2'):
            raise serializers.ValidationError("Os e-mails não coincidem.")
        return data

    def create(self, validated_data):
        validated_data.pop('email2', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            password=validated_data['password'],
            is_active=False,  # Usuário inicialmente inativo
        )
        send_confirmation_email(user)
        return user

def send_confirmation_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"{settings.FRONTEND_URL}/ativar-conta/{uid}/{token}/"
    subject = "Confirme seu cadastro"
    message = (
        f"Olá {user.first_name or user.username},\n\n"
        "Por favor, clique no link abaixo para ativar sua conta:\n"
        f"{activation_link}\n\n"
        "Se você não se cadastrou, ignore este e-mail."
    )
    html_message = (
        f"<p>Olá {user.first_name or user.username},</p>"
        "<p>Por favor, clique no link abaixo para ativar sua conta:</p>"
        f"<p><a href=\"{activation_link}\">{activation_link}</a></p>"
        "<p>Se você não se cadastrou, ignore este e-mail.</p>"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )

    