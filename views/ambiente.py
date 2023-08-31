import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from guardian.mixins import LoginRequiredMixin
from rest_framework import status
from app.edificaciones.models import Ambiente

from api.response import get_response
from app.core.layer.application.campus_app_service import CampusAppService
from app.core.layer.application.core_app_service import CoreAppService
from app.core.utils.enums import MensajesEnum
from app.edificaciones.forms.ambiente import AmbienteEditarForm, SubambienteEditarForm, AmbienteCrearForm, \
    AmbienteUsoEditarForm
from app.edificaciones.layer.application.bloque_app_service import BloqueAppService #borrar, es solo para probar
from app.edificaciones.layer.application.ambiente_app_service import AmbienteAppService
from app.edificaciones.layer.application.ambiente_uso_app_service import AmbienteUsoAppService
from app.edificaciones.layer.application.dependencia_app_service import DependenciaAppService
from app.edificaciones.layer.security.ambiente_sec_service import AmbienteSecService
from app.edificaciones.layer.security.ambiente_uso_sec_service import AmbienteUsoSecService
from app.edificaciones.models import Ambiente, Subambiente, AmbienteUso, Recurso
from app.edificaciones.models import Bloque, Dependencia
from app.core.models import Campus
from app.planificacion.views.mixins import AjaxTemplateMixin, CreateViewSiaaf, UpdateViewSiaaf, DeleteViewSiaaf


@login_required
def index(request):
    return render(request, 'edificaciones/index.html', locals())


class AmbienteCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Ambiente
    form_class = AmbienteCrearForm

    def get_success_url(self):
        ambiente_uso = self.object.ambiente_usos.first()
        if ambiente_uso:
            return reverse('edificaciones:ambiente_uso_detalle', args=[ambiente_uso.id])

        return reverse('edificaciones:ambiente_detalle', args=[self.object.id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_ambiente')

    def post(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save(commit=False)
            AmbienteAppService.crear(self.object, self.request.user, self.request.POST)
            messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

            if CoreAppService.es_ajax(request):
                return get_response(data={'success_url': self.get_success_url()})

            return redirect(self.get_success_url())

        return self.render_to_response(context)


class AmbienteEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Ambiente
    form_class = AmbienteEditarForm

    def get_success_url(self):
        return reverse('edificaciones:ambiente_detalle', args=[self.get_object().id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.change_ambiente')


class AmbienteEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Ambiente

    def get_success_url(self):
        return reverse('edificaciones:ambiente_lista')

    def test_func(self):
        return self.request.user.has_perm('edificaciones.delete_ambiente')


class AmbienteDetalle(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Ambiente
    template_name = 'edificaciones/ambiente/detalle.html'

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_ambiente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_editar'] = AmbienteSecService.puede_editar(
            self.request.user, self.get_object())
        context['puede_eliminar'] = AmbienteSecService.puede_eliminar(
            self.request.user, self.get_object())
        return context


class AmbienteLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
#definición de clase y configuración inicial
    model = Ambiente
    template_name = 'edificaciones/ambiente/lista.html'
    #Inicializa el queryset de la vista como vacío. Esto se hace para evitar que la vista cargue automáticamente todas las instancias de Ambiente.
    queryset = Ambiente.objects.none()

#manejo de permisos y autenticación
    #Esta anotación se utiliza para eximir a la vista de la protección CSRF (Cross-Site Request Forgery)
    @method_decorator(csrf_exempt)
    #Esta función es un método de Django que controla el procesamiento de la solicitud antes de que llegue al método específico de la vista
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    #Esta función se llama cuando un usuario no tiene los permisos requeridos para acceder a la vista o es solicitud AJAX o no.
    def handle_no_permission(self):
        if not CoreAppService.es_ajax(self.request):
            return super().handle_no_permission()

        if self.request.user.is_authenticated:
            return get_response(mensaje=MensajesEnum.MSG_NO_PERMITIDO.value,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return get_response(mensaje=MensajesEnum.MSG_SESION_CADUCADA.value,
                                status=status.HTTP_401_UNAUTHORIZED)
    #Esta función es utilizada por las clases basadas en permisos de Django para determinar si un usuario tiene permiso para acceder a la vista
    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_ambiente')

#obtención de datos y contexto
    #Esta función se utiliza para obtener el contexto de datos que se pasará al template al renderizar la vista.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campus'] = CampusAppService.get_lista()
        context['dependencias'] = DependenciaAppService.get_lista()
        return context


    def get(self, request, *args, **kwargs):
        if CoreAppService.es_ajax(request):
            data = AmbienteAppService.get_lista_filter(request, request.GET)
            
            return JsonResponse(data)
        else:
            return super(AmbienteLista, self).get(request, *args, **kwargs)


class AmbienteUsoCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = AmbienteUso
    form_class = AmbienteUsoEditarForm
    ajax_template_name = 'edificaciones/ambiente_uso/modal_editar.html'

    def get_ambiente(self):
        return Ambiente.objects.get(pk=self.kwargs.get('ambiente_id'))

    def get_initial(self):
        initial = super(AmbienteUsoCrear, self).get_initial()
        ambiente = self.get_ambiente()
        initial['ambiente'] = ambiente
        initial['usuario'] = self.request.user
        initial['ambiente_uso'] = AmbienteAppService.get_uso_actual(ambiente)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ambiente = self.get_ambiente()
        ambiente_uso = AmbienteUso(ambiente=ambiente, usuario=self.request.user,
                                   ambiente_uso=AmbienteAppService.get_uso_actual(ambiente),
                                   revision_fecha=datetime.datetime.now())
        context['ambienteuso'] = ambiente_uso

        return context

    def get_success_url(self):
        return reverse('edificaciones:ambiente_uso_detalle', args=[self.object.id])

    def test_func(self):
        return self.request.user.has_perm('edificaciones.add_ambienteuso')

    def post(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():

            self.object = form.save(commit=False)
            self.object.revision_fecha = datetime.datetime.now()
            self.object.revision_anio = datetime.datetime.now().year

            AmbienteUsoAppService.actualizar(self.object)
            AmbienteUsoAppService.aula_crear_o_editar(self.object, self.request.POST)

            messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

            if CoreAppService.es_ajax(request):
                return get_response(data={'success_url': self.get_success_url()})

            return redirect(self.get_success_url())

        return self.render_to_response(context)


class AmbienteUsoEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = AmbienteUso
    form_class = AmbienteUsoEditarForm
    ajax_template_name = 'edificaciones/ambiente_uso/modal_editar.html'

    def get_success_url(self):
        return reverse('edificaciones:ambiente_uso_detalle', args=[self.object.id])

    def get_ambiente(self):
        return self.object.ambiente

    def test_func(self):
        return AmbienteUsoSecService.puede_editar(self.request.user, self.get_object())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():

            self.object = form.save(commit=False)
            AmbienteUsoAppService.actualizar(self.object)
            AmbienteUsoAppService.aula_crear_o_editar(self.object, self.request.POST)

            messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

            if CoreAppService.es_ajax(request):
                return get_response(data={'success_url': self.get_success_url()})

            return redirect(self.get_success_url())

        return self.render_to_response(context)


class AmbienteUsoEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = AmbienteUso

    def get_success_url(self):
        ambiente = self.object.ambiente
        AmbienteAppService.actualizar_uso_actual(ambiente)
        return reverse('edificaciones:ambiente_detalle', args=[ambiente.id])

    def test_func(self):
        return AmbienteUsoSecService.puede_eliminar(self.request.user, self.get_object())


class AmbienteUsoDetalle(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AmbienteUso
    template_name = 'edificaciones/ambiente_uso/detalle.html'

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_ambienteuso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ambiente_uso = self.get_object()
        puede_editar = AmbienteUsoSecService.puede_editar(
            self.request.user, ambiente_uso)

        context['puede_editar'] = puede_editar
        context['puede_eliminar'] = AmbienteUsoSecService.puede_eliminar(self.request.user, ambiente_uso)
        context['recursos'] = AmbienteUsoAppService.get_recursos(ambiente_uso, puede_editar)
        context['aula'] = AmbienteUsoAppService.aula_get(ambiente_uso)

        return context


class AmbienteUsoLista(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AmbienteUso
    template_name = 'edificaciones/ambiente_uso/fragmento_lista.html'
    queryset = AmbienteUso.objects.none()

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

    def get_ambiente(self):
        return Ambiente.objects.get(pk=self.kwargs.get('ambiente_id'))

    def test_func(self):
        return self.request.user.has_perm('edificaciones.view_ambiente')

    def get(self, request, *args, **kwargs):
        # se utiliza desde detalle del ambiente
        if CoreAppService.es_ajax(request):
            data = AmbienteUsoAppService.get_lista_filter(
                request, self.get_ambiente(), request.GET)
            return JsonResponse(data)
        else:
            return super(AmbienteUsoLista, self).get(request, *args, **kwargs)

@login_required
@require_http_methods(["GET"])
def obtener_anios_revisiones(request):
    ambiente_usos = AmbienteUso.objects.all()
    unique_years = ambiente_usos.values_list('revision_anio', flat=True).distinct()
    print("años",unique_years)
    return JsonResponse({'unique_years': list(unique_years)})



@login_required
@require_http_methods(["POST"])
def ambiente_uso_recursos_guardar(request, ambiente_uso_id, recurso_id):

    data = request.POST
    ambiente_uso = AmbienteUso.objects.get(id=ambiente_uso_id)
    recurso = Recurso.objects.get(id=recurso_id)
    puede_editar = AmbienteUsoSecService.puede_editar(
        request.user, ambiente_uso)

    if puede_editar:

        # Proceso la data del formulario
        respuestas = {}
        for item in data:
            if 'recurso_item' in item:
                label, id_recurso_item = item.split('|')
                respuestas[id_recurso_item] = data[item]

        AmbienteUsoAppService.guardar_recursos(
            ambiente_uso, recurso, respuestas)

        return redirect(reverse('edificaciones:ambiente_uso_detalle', args=[ambiente_uso_id]))

    messages.error(request, MensajesEnum.MSG_NO_PERMITIDO.value)
    return redirect(reverse('index'))


class SubambienteCrear(UserPassesTestMixin, AjaxTemplateMixin, CreateViewSiaaf):
    model = Subambiente
    form_class = SubambienteEditarForm

    def get_ambiente_uso(self):
        return AmbienteUso.objects.get(pk=self.kwargs.get('ambiente_uso_id'))

    def get_success_url(self):
        return reverse('edificaciones:ambiente_uso_detalle', args=[self.get_ambiente_uso().id])

    def test_func(self):
        return AmbienteUsoSecService.puede_editar(self.request.user, self.get_ambiente_uso())

    def get_initial(self):
        initial = super(SubambienteCrear, self).get_initial()
        initial['ambiente_uso'] = self.get_ambiente_uso()
        return initial

    def post(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():

            self.object = form.save()
            AmbienteUsoAppService.actualizar(self.object.ambiente_uso)
            messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

            if CoreAppService.es_ajax(request):
                return get_response(data={'success_url': self.get_success_url()})

            return redirect(self.get_success_url())

        return self.render_to_response(context)


class SubambienteEditar(UserPassesTestMixin, AjaxTemplateMixin, UpdateViewSiaaf):
    model = Subambiente
    form_class = SubambienteEditarForm

    def get_ambiente_uso(self):
        return self.get_object().ambiente_uso

    def get_success_url(self):
        return reverse('edificaciones:ambiente_uso_detalle', args=[self.get_ambiente_uso().id])

    def test_func(self):
        return AmbienteUsoSecService.puede_editar(self.request.user, self.get_ambiente_uso())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():

            self.object = form.save()
            AmbienteUsoAppService.actualizar(self.object.ambiente_uso)
            messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

            if CoreAppService.es_ajax(request):
                return get_response(data={'success_url': self.get_success_url()})

            return redirect(self.get_success_url())

        return self.render_to_response(context)


class SubambienteEliminar(LoginRequiredMixin, UserPassesTestMixin, DeleteViewSiaaf):
    model = Subambiente

    def get_success_url(self):
        ambiente_uso = self.object.ambiente_uso
        AmbienteUsoAppService.actualizar(ambiente_uso)
        return reverse('edificaciones:ambiente_uso_detalle', args=[ambiente_uso.id])

    def test_func(self):
        return AmbienteUsoSecService.puede_editar(self.request.user, self.get_object().ambiente_uso)
