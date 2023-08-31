from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


from app.core.models import AuditModel


class Dependencia(AuditModel):
    nombre = models.CharField(max_length=100)
    siglas = models.CharField(max_length=25)

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.siglas)


class Bloque(AuditModel):
    CHOICE_PISOS = [(nro, nro) for nro in list(range(1, 11))]  # 1 al 10

    numero = models.PositiveSmallIntegerField(validators=[MinValueValidator(
        1), MaxValueValidator(250)], verbose_name='Número de bloque')  # 1 al 250
    numero_pisos = models.PositiveSmallIntegerField(choices=CHOICE_PISOS)

    campus = models.ForeignKey(
        'core.Campus', related_name='bloques', on_delete=models.PROTECT)

    class Meta:
        ordering = ['campus__nombre', 'numero']
        constraints = [models.UniqueConstraint(
            fields=['campus', 'numero'], name='Unico por campus y numero')]

    def __str__(self):
        return 'Sede %s - Campus %s (%s) - Bloque %s' % (self.campus.sede.nombre, self.campus.nombre, self.campus.codigo, self.numero)


class Recurso(AuditModel):
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    orden = models.SmallIntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['orden']


class RecursoItem(AuditModel):
    TIPO_NUMERO = 'NÚMERO'
    TIPO_BOOLEANO = 'BOOLEANO'
    TIPO_CATALOGO = 'CATALOGO'
    TIPO_TEXTO = 'TEXTO'
    CHOICE_TIPO = ((TIPO_NUMERO, 'Número'),
                   (TIPO_BOOLEANO, 'Verdadero/Falso'),
                   (TIPO_CATALOGO, 'Catálogo'),
                   (TIPO_TEXTO, 'Texto'))
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(choices=CHOICE_TIPO, max_length=20)
    orden = models.SmallIntegerField()

    catalogo = models.ForeignKey('core.Catalogo', null=True, blank=True,
                                 related_name='recursos', on_delete=models.PROTECT)  # cuando es tipo catalogo
    recurso = models.ForeignKey(
        'Recurso', related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['orden']
        constraints = [
            models.UniqueConstraint(
                fields=['recurso', 'nombre'], name='Único por recurso y nombre')
        ]


class UsoTipo(AuditModel):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=25)
    caracteristica = models.CharField(max_length=500)
    aula = models.BooleanField(default=False, verbose_name='Es de tipo aula')

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.codigo)
