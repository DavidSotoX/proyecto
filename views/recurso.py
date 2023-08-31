from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from guardian.mixins import LoginRequiredMixin
from rest_framework import status

from api.response import get_response
from app.core.utils.enums import MensajesEnum
from app.edificaciones.forms.recurso import RecursoEditarForm
from app.edificaciones.forms.recurso import RecursoItemEditarForm
from app.edificaciones.layer.application.recurso_app_service import RecursoAppService
from app.edificaciones.models import Recurso, RecursoItem
from app.planificacion.views.mixins import AjaxTemplateMixin, CreateViewSiaaf, UpdateViewSiaaf, DeleteViewSiaaf
from app.core.layer.application.core_app_service import CoreAppService

class RecursoLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Recurso
    template_name = 'edificaciones/recurso/lista.html'
    queryset = Recurso.objects.none()

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
        return self.request.user.has_perm('edificaciones.view_recurso')

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = RecursoAppService.get_lista_filter(
                request, request.GET)
            return JsonResponse(data)
        else:
            return super(RecursoLista, self).get(request, *args, **kwargs)


class RecursoCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Recurso
    form_class = RecursoEditarForm

    def get_success_url(self):
        return reverse('edificaciones:recurso_detalle', args=[self.object.id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_recurso')


class RecursoEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Recurso
    form_class = RecursoEditarForm

    def get_success_url(self):
        return reverse('edificaciones:recurso_detalle', args=[self.get_object().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.change_recurso')


class RecursoEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Recurso

    def get_success_url(self):
        return reverse('edificaciones:recurso_lista')

    def test_func(self):
        return self.request.user.has_perm('edificaciones.delete_recurso')


class RecursoDetalle(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Recurso
    template_name = 'edificaciones/recurso/detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['CHOICE_TIPO'] = RecursoItem.CHOICE_TIPO
        return context

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_recurso')


class RecursoItemLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RecursoItem
    template_name = 'edificaciones/recursoitem/fragmento_lista.html'
    queryset = RecursoItem.objects.none()

    def get_recurso(self):
        return Recurso.objects.get(pk=self.kwargs.get('recurso_id'))

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
        return self.request.user.has_perm('edificaciones.view_recursoitem') if CoreAppService.es_ajax(self.request) else False

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = RecursoAppService.get_items_lista_filter(
                request, request.GET, self.get_recurso())
            return JsonResponse(data)
        else:
            return super(RecursoItemLista, self).get(request, *args, **kwargs)


class RecursoItemCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = RecursoItem
    form_class = RecursoItemEditarForm

    def get_recurso(self):
        return Recurso.objects.get(pk=self.kwargs.get('recurso_id'))

    def get_success_url(self):
        return reverse('edificaciones:recurso_detalle', args=[self.get_recurso().id])

    def get_initial(self):
        initial = super(RecursoItemCrear, self).get_initial()
        initial['recurso'] = self.get_recurso()
        return initial

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_recursoitem')


class RecursoitemEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = RecursoItem
    form_class = RecursoItemEditarForm

    def get_recurso(self):
        return self.get_object().recurso

    def get_success_url(self):
        return reverse('edificaciones:recurso_detalle', args=[self.get_recurso().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.change_recursoitem')


class RecursoItemEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = RecursoItem

    def get_recurso(self):
        return self.object.recurso

    def get_success_url(self):
        return reverse('edificaciones:recurso_detalle', args=[self.get_recurso().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.delete_recursoitem')
