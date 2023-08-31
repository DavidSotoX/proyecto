from django.core.validators import MinValueValidator
from django.db import models

from app.core.layer.application.catalogo_item_app_service import CatalogoItemAppService
from app.core.models import CatalogoItem
from app.edificaciones.models import Bloque, RecursoItem
from app.seguridad.models import Usuario, AuditModel


class Ambiente(AuditModel):
    revision_anio_actual = models.CharField(max_length=4, null=True, blank=True)  # revision_anio actual de AmbienteUso
    codigo_actual = models.CharField(max_length=50, null=True, blank=True) # codigo_display actual de AmbienteUso
    descripcion = models.CharField(max_length=250, verbose_name='Descripción')
    numero_piso = models.PositiveSmallIntegerField(choices=Bloque.CHOICE_PISOS, verbose_name='Número de piso')
    uso_finicio = models.DateField(null=True, blank=True)
    uso_ffin = models.DateField(null=True, blank=True)

    dependencia_actual = models.ForeignKey('Dependencia', related_name='ambientes', on_delete=models.PROTECT, null=True) #  dependencia actual de AmbienteUso
    bloque = models.ForeignKey('Bloque', related_name='ambientes', on_delete=models.PROTECT)

    class Meta:
        ordering = ['bloque__campus__nombre', 'bloque__numero', 'numero_piso', 'descripcion']
        constraints = [models.UniqueConstraint(fields=['bloque', 'numero_piso', 'descripcion'], name='Unico por bloque, número de piso y descripción')]

    def __str__(self):
        return '%s - Ambiente %s' % (self.get_ubicacion(), self.descripcion)

    def get_ubicacion(self):
        return '%s - Piso %s' % (str(self.bloque), self.numero_piso)


class AmbienteUso(AuditModel):

    area = models.DecimalField(max_digits=10, decimal_places=2) # metros cuadrados y aceptando dos decimales
    ancho = models.FloatField()
    alto = models.FloatField()
    codigo_anterior = models.CharField(max_length=50) # incluye codigo completo del ambiente_uso, si es el primero se ingresa de forma manual
    codigo = models.CharField(max_length=25, verbose_name='Código')  # incluye caracteres y numeros
    codigo_display = models.CharField(max_length=50)  # incluye codigo completo
    codigo_puerta = models.BooleanField()
    largo = models.FloatField()
    observacion = models.TextField(max_length=200, null=True, blank=True)
    revision_fecha = models.DateTimeField()
    revision_anio = models.CharField(max_length=4)

    ambiente_uso = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True) # uso anterior
    ambiente = models.ForeignKey('Ambiente', related_name='ambiente_usos', on_delete=models.PROTECT)
    dependencia = models.ForeignKey('Dependencia', related_name='ambiente_usos', on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, related_name='ambiente_usos', on_delete=models.PROTECT)
    uso_tipo = models.ForeignKey('UsoTipo', related_name='ambiente_usos', on_delete=models.PROTECT)
    
    class Meta:
        ordering = ['revision_anio']

    def __str__(self):
        return '%s - Revisión %s (%s)' % (str(self.ambiente), self.codigo_display, self.revision_anio)

    def get_codigo_display(self):
        codigo_base = '%s.%s.%s.%s' % (self.ambiente.bloque.campus.codigo, self.ambiente.bloque.numero, self.ambiente.numero_piso, self.codigo)
        subcodigos = '.'.join([str(item) for item in self.subambientes.values_list('codigo', flat=True)])
        return '%s%s' % (codigo_base, '.%s' % subcodigos if subcodigos else '')

class Subambiente(AuditModel):
    codigo = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Código')
    nombre = models.CharField(max_length=500)

    ambiente_uso = models.ForeignKey('AmbienteUso', related_name='subambientes', on_delete=models.PROTECT)

    class Meta:
        ordering = ['codigo']
        constraints = [models.UniqueConstraint(fields=['ambiente_uso', 'codigo'], name='Unico por ambiente y código')]

    def __str__(self):
        return '%s - Subambiente %s (%s)' % (str(self.ambiente_uso), self.nombre, self.codigo)

class AmbienteRecurso(AuditModel):

    ambiente_uso = models.ForeignKey('AmbienteUso', related_name='recursos', on_delete=models.PROTECT)
    recurso = models.ForeignKey('Recurso', related_name='ambiente_recursos', on_delete=models.PROTECT)

class AmbienteItem(AuditModel):
    valor = models.CharField(max_length=1000)

    ambiente_recurso = models.ForeignKey('AmbienteRecurso', related_name='items', on_delete=models.PROTECT)
    recurso_item = models.ForeignKey('RecursoItem', related_name='ambiente_items', on_delete=models.PROTECT)

    def get_valor(self):
        if self.recurso_item.tipo == RecursoItem.TIPO_CATALOGO:
            catalogo_item = CatalogoItem.objects.get(id=self.valor)
            return catalogo_item.nombre

        return self.valor

class Aula(AuditModel):
    distancia_primera_fila = models.FloatField(verbose_name='Distancia de primera fila a la pizarra (Z)')
    area_por_alumno = models.FloatField(verbose_name='Área asignada por alumno (As)')
    capacidad_alumnos = models.PositiveIntegerField(verbose_name='Capacidad Teórica de Alumnos (Ca)')

    ambiente_uso = models.OneToOneField('AmbienteUso', on_delete=models.CASCADE)

    def __str__(self):
        return f'Aula ID: {self.id}'