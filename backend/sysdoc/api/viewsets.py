from rest_framework.viewsets import ModelViewSet
from sysdoc.models import (Processo, UsuarioDocs,
                           TarefaProcesso, Itemizacao,
                           UsuarioProcesso)

from .serializers import (
    CustomTokenObtainPairSerializer,
    ProcessoSerializer, UsuarioDocsSerializer,
    TarefaProcessoSerializer, ItemizacaoSerializer,
    UsuarioProcessoSerializer, ProcessoTreeUsuarioSerializer,
    UserSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ---- NOVOS VIEWSETS PARA PROCESSO ---- #
class ProcessoViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Processo.objects.all().order_by('id')
    serializer_class = ProcessoSerializer

# ---- NOVOS VIEWSETS PARA TAREFA-PROCESSO ---- #
class TarefaProcessoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TarefaProcesso.objects.all().order_by('id')

    def get_serializer_class(self):
        # Usa o ListSerializer para criação e atualização
        if self.action in ['list', 'create', 'update', 'partial_update']:
            return TarefaProcessoSerializer
        return TarefaProcessoSerializer

# ---- NOVOS VIEWSETS PARA ITEMIZAÇÃO ---- #
class ItemizacaoViewSet(ModelViewSet):
    """
    ViewSet para CRUD de Itemização.
    - Para criação e edição, usa o serializer que aceita 'processo' e 'itemSuperior'.
    - Para retrieve, retorna árvore detalhada (com subitemizações e tarefas).
    """
    permission_classes = [IsAuthenticated]
    queryset = Itemizacao.objects.all().order_by('id')

    def get_serializer_class(self):
        # Usa ListSerializer para criação, listagem e atualização (aceita 'processo')
        if self.action in ['list', 'create', 'update', 'partial_update']:
            return ItemizacaoSerializer
        # Usa detalhado para retrieve (GET /itemizacao/<id>/)
        return ItemizacaoSerializer

    # Exemplo de ação customizada (opcional):
    @action(detail=False, methods=['get'], url_path='por-processo/(?P<processo_id>[^/.]+)')
    def por_processo(self, request, processo_id=None):
        """
        Lista todas as itemizações de um processo (opcional).
        """
        queryset = Itemizacao.objects.filter(processo_id=processo_id).order_by('id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UsuarioDocsViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UsuarioDocs.objects.all().order_by('id')
    serializer_class = UsuarioDocsSerializer

    # Ação customizada para filtrar por usuário, tarefaProcesso e usuarioProcesso
    @action(detail=False, methods=['get'])
    def filtro_por_usuario_tarefa_usuarioProcesso(self, request):
        # Obtendo os parâmetros da URL
        tarefa_id = request.query_params.get('tarefa', None)
        usuario_processo_id = request.query_params.get('usuarioProcesso', None)

        # Corrigido: inicializar queryset ordenado
        queryset = self.get_queryset()

        # Aplicando os filtros se os parâmetros forem fornecidos
        if tarefa_id:
            queryset = queryset.filter(tarefaProcesso_id=tarefa_id)

        if usuario_processo_id:
            queryset = queryset.filter(usuarioProcesso_id=usuario_processo_id)

        # Serializando e retornando os dados
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# ---- NOVOS VIEWSETS PARA USUARIO-PROCESSO ---- #
class UsuarioProcessoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = UsuarioProcesso.objects.all().order_by('id')
    serializer_class = UsuarioProcessoSerializer

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """
        ViewSet utilizado para listar os processos do usuário
        """
        user = get_object_or_404(User, id=user_id)
        usuario_processos = UsuarioProcesso.objects.filter(usuario=user).order_by('id')
        serializer = UsuarioProcessoSerializer(usuario_processos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='processo-tree')
    def processo_tree(self, request, pk=None):
        """
        Retorna a estrutura de processo (itemizações, subitemizações, tarefas) com documentos e pontos já computados para este UsuarioProcesso.
        Inclui também o campo link_processo_pdf.
        """
        usuario_processo = get_object_or_404(UsuarioProcesso, id=pk)
        processo = usuario_processo.processo
        serializer = ProcessoTreeUsuarioSerializer(
            processo,
            context={'usuario_processo': usuario_processo, 'request': request}
        )
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        # Atualiza o log concatenado se enviado
        if 'log' in data:
            old_log = instance.log or ""
            new_log = data['log'].strip()
            if old_log.strip():
                data['log'] = f"{old_log.strip()}\n{new_log}"
            else:
                data['log'] = new_log

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

# ---- NOVOS VIEWSETS PARA USUÁRIO ---- #
class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Não autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Não autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {"detail": "Você não pode apagar o próprio usuário logado."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)