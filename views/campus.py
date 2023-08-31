from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from guardian.mixins import LoginRequiredMixin
from rest_framework import status
from app.core.layer.application.core_app_service import CoreAppService
from api.response import get_response
from app.core.layer.application.campus_app_service import CampusAppService
from app.core.layer.application.sede_app_service import SedeAppService
from app.core.models import Campus
from app.core.utils.enums import MensajesEnum
from app.edificaciones.forms.campus import CampusEditarForm, BloqueEditarForm
from app.edificaciones.layer.application.bloque_app_service import BloqueAppService
from app.edificaciones.models import Bloque
from app.planificacion.views.mixins import AjaxTemplateMixin, CreateViewSiaaf, UpdateViewSiaaf, DeleteViewSiaaf


@login_required
def index(request):
    return render(request, 'edificaciones/index.html', locals())

class CampusCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Campus
    form_class = CampusEditarForm

    def get_success_url(self):
        return reverse('edificaciones:campus_detalle', args=[self.object.id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_campus')

class CampusDetalle(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Campus
    template_name = 'edificaciones/campus/detalle.html'

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_campus')

class CampusEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Campus
    form_class = CampusEditarForm

    def get_success_url(self):
        return reverse('edificaciones:campus_detalle', args=[self.get_object().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.change_campus')

class CampusEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Campus

    def get_success_url(self):
        return reverse('edificaciones:campus_lista')

    def test_func(self):
        return self.request.user.has_perm('edificaciones.delete_campus')

class CampusLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Campus
    template_name = 'edificaciones/campus/lista.html'
    queryset = Campus.objects.none()

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
        return self.request.user.has_perm('edificaciones.view_campus')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sedes'] = SedeAppService.get_lista()
        return context

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = CampusAppService.get_lista_filter(request, request.GET)
            return JsonResponse(data)
        else:
            return super(CampusLista, self).get(request, *args, **kwargs)

@login_required
@require_http_methods(["GET"])
def campus_bloques(request, campus_id):
    """
    Lista los bloques de un campus (filtro lista de ambientes)
    :param request:
    :param id:
    :return:
    """
    if request.user.has_perm('edificaciones.view_ambiente'):
        campus = Campus.objects.get(id=campus_id)
        bloques = BloqueAppService.get_lista_por_campus(campus).values('id', 'numero')
        return get_response(data=list(bloques))

    return get_response(status=status.HTTP_401_UNAUTHORIZED,
                        mensaje=MensajesEnum.MSG_NO_PERMITIDO.value)

class BloqueCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Bloque
    form_class = BloqueEditarForm

    def get_campus(self):
        return Campus.objects.get(pk=self.kwargs.get('campus_id'))

    def get_success_url(self):
        return reverse('edificaciones:campus_detalle', args=[self.get_campus().id])

    def get_initial(self):
        initial = super(BloqueCrear, self).get_initial()
        initial['campus'] = self.get_campus()
        return initial

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_bloque')

class BloqueEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Bloque
    form_class = BloqueEditarForm

    def get_campus(self):
        return self.get_object().campus

    def get_success_url(self):
        return reverse('edificaciones:campus_detalle', args=[self.get_campus().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.change_bloque')

class BloqueEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Bloque

    def get_campus(self):
        return self.object.campus

    def get_success_url(self):
        return reverse('edificaciones:campus_detalle', args=[self.get_campus().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.delete_bloque')

class BloqueLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Bloque
    template_name = 'edificaciones/bloque/fragmento_lista.html'
    queryset = Bloque.objects.none()

    def get_campus(self):
        return Campus.objects.get(pk=self.kwargs.get('campus_id'))

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
        return self.request.user.has_perm('edificaciones.view_bloque') if CoreAppService.es_ajax(self.request) else False

    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = BloqueAppService.get_lista_filter(request, request.GET, self.get_campus())
            return JsonResponse(data)
        else:
            return super(BloqueLista, self).get(request, *args, **kwargs)


@login_required
@require_http_methods(["GET"])
def bloque_pisos(request, bloque_id):
    """
    Lista los pisos que le corresponde a un bloque (crear ambiente, editar ambiente, filtro lista de ambientes)
    :param request:
    :param id:
    :return:
    """
    if request.user.has_perm('edificaciones.add_ambiente') or request.user.has_perm('edificaciones.change_ambiente'):
        bloque = Bloque.objects.get(id=bloque_id)
        pisos = BloqueAppService.get_pisos_lista(bloque)
        return get_response(data=pisos)

    return get_response(status=status.HTTP_401_UNAUTHORIZED,
                        mensaje=MensajesEnum.MSG_NO_PERMITIDO.value)