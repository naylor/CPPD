from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sysdoc.api.viewsets import (CustomTokenObtainPairView, 
                                 UsuarioDocsViewSet,
                                 UsuarioProcessoViewSet,
                                 ProcessoViewSet, 
                                 TarefaProcessoViewSet, ItemizacaoViewSet,
                                 UserViewSet
)
from rest_framework_simplejwt import views as jwt_views
from sysdoc.views import (gerar_pdf_processo, activate_user, 
                          ChangePasswordView, ResendActivationView,
                          ArvoreView)
from django.conf.urls.static import static
from django.conf import settings


router = DefaultRouter()
router.register(r'processo', ProcessoViewSet, basename='processo')
router.register(r'tarefa-processo', TarefaProcessoViewSet, basename='tarefa-processo')
router.register(r'itemizacao', ItemizacaoViewSet, basename='itemizacao')
router.register(r'usuario', UserViewSet, basename='usuario')
router.register(r'usuario-processo', UsuarioProcessoViewSet)
router.register(r'usuario-docs', UsuarioDocsViewSet, basename='usuario-docs')

urlpatterns = [
path(
        'gerar_pdf/<uuid:processo_id>/<int:usuario_id>/<uuid:usuario_process_id>/',
        gerar_pdf_processo,
        name='gerar_pdf_processo'
    ),
    path('processo/<uuid:processo_id>/arvore/', ArvoreView.as_view(), name='arvore-proc'),
    path('admin/', admin.site.urls),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('activate/<uidb64>/<token>/', activate_user, name='activate-user'),
    path('resend-activation/', ResendActivationView.as_view(), name='resend-activation'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)