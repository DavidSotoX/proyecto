from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from guardian.mixins import LoginRequiredMixin
from rest_framework import status

from api.response import get_response
from app.core.models import Catalogo, CatalogoItem
from app.core.utils.enums import MensajesEnum
from app.edificaciones.forms.catalogo import CatalogoEditarForm
from app.edificaciones.forms.catalogo import CatalogoItemEditarForm
from app.edificaciones.layer.application.catalogo_app_service import CatalogoAppService
from app.planificacion.views.mixins import AjaxTemplateMixin, CreateViewSiaaf, UpdateViewSiaaf, DeleteViewSiaaf
from app.core.layer.application.core_app_service import CoreAppService


class CatalogoLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Catalogo
    template_name = 'edificaciones/catalogo/lista.html'
    queryset = Catalogo.objects.none()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if not CoreAppService.es_ajax(self.request):
            return super().handle_no_permission()

        if self.request.user.is_authenticated:
            return get_response(mensaje=MensajesEnum.MSG_NO_PERMITIDO.value,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return get_response(mensaje=MensajesEnum.MSG_SESION_CADUCADA.value,
                                status=status.HTTP_401_UNAUTHORIZED)

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_catalogo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = CatalogoAppService.get_lista_filter(
                request, request.GET)
            return JsonResponse(data)
        else:
            return super(CatalogoLista, self).get(request, *args, **kwargs)


class CatalogoCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Catalogo
    form_class = CatalogoEditarForm

    def get_success_url(self):
        return reverse('edificaciones:catalogo_detalle', args=[self.object.id])

    def test_func(self):
        return self.request.user.has_perm('core.add_catalogo')

    def form_valid(self, form):
        # Establecer el valor predeterminado de app
        form.instance.app = CatalogoAppService.app
        form.instance.version = 1
        return super().form_valid(form)


class CatalogoEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Catalogo
    form_class = CatalogoEditarForm

    def get_success_url(self):
        return reverse('edificaciones:catalogo_detalle', args=[self.get_object().id])

    def test_func(self):
        return self.request.user.has_perm('core.change_catalogo')


class CatalogoEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Catalogo

    def get_success_url(self):
        return reverse('edificaciones:catalogo_lista')

    def test_func(self):
        return self.request.user.has_perm('core.delete_catalogo')


class CatalogoDetalle(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Catalogo
    template_name = 'edificaciones/catalogo/detalle.html'

    def test_func(self):
        return self.request.user.has_perm('core.view_catalogo')


class CatalogoItemLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CatalogoItem
    template_name = 'edificaciones/catalogoitem/fragmento_lista.html'
    queryset = CatalogoItem.objects.none()

    def get_catalogo(self):
        return Catalogo.objects.get(pk=self.kwargs.get('catalogo_id'))

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return get_response(mensaje=MensajesEnum.MSG_NO_PERMITIDO.value,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return get_response(mensaje=MensajesEnum.MSG_SESION_CADUCADA.value,
                                status=status.HTTP_401_UNAUTHORIZED)

    def test_func(self):
        return self.request.user.has_perm('core.view_catalogoitem') if CoreAppService.es_ajax(self.request) else False

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = CatalogoAppService.get_items_lista_filter(
                request, request.GET, self.get_catalogo())
            return JsonResponse(data)
        else:
            return super(CatalogoItemLista, self).get(request, *args, **kwargs)


class CatalogoitemCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = CatalogoItem
    form_class = CatalogoItemEditarForm

    def get_catalogo(self):
        return Catalogo.objects.get(pk=self.kwargs.get('catalogo_id'))

    def get_success_url(self):
        return reverse('edificaciones:catalogo_detalle', args=[self.get_catalogo().id])

    def get_initial(self):
        initial = super(CatalogoitemCrear, self).get_initial()
        initial['catalogo'] = self.get_catalogo()
        return initial

    def test_func(self):
        return self.request.user.has_perm('core.add_catalogoitem')


class CatalogoitemEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = CatalogoItem
    form_class = CatalogoItemEditarForm

    def get_catalogo(self):
        return self.get_object().catalogo

    def get_success_url(self):
        return reverse('edificaciones:catalogo_detalle', args=[self.get_catalogo().id])

    def test_func(self):
        return self.request.user.has_perm('core.change_catalogoitem')


class CatalogoitemEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = CatalogoItem

    def get_catalogo(self):
        return self.object.catalogo

    def get_success_url(self):
        return reverse('edificaciones:catalogo_detalle', args=[self.get_catalogo().id])

    def test_func(self):
        return self.request.user.has_perm('core.delete_catalogoitem')
