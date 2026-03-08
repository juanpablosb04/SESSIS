# reportes/models.py
from django.db import models

CATEGORIAS = (
    ("accidente-trabajo", "Accidente de trabajo"),
    ("fallo-equipamiento", "Fallo de equipamiento"),
    ("incidente-seguridad", "Incidente de seguridad"),
    ("problema-ambiental", "Problema ambiental"),
    ("otros-eventos", "Otros eventos"),
)

class ReporteIncidente(models.Model):
    id_reporte   = models.AutoField(primary_key=True)
    # la FK apunta a empleados.Empleado y la columna real en SQL se llama id_empleado
    id_empleado  = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.DO_NOTHING,
        db_column='id_empleado',
        related_name='reportes_incidentes',
    )
    categoria    = models.CharField(max_length=50, choices=CATEGORIAS)
    # la columna real para la imagen se llama 'archivo'
    foto         = models.ImageField(upload_to='incidentes/', db_column='archivo', blank=True, null=True)
    fecha_evento = models.DateField()
    descripcion  = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ReporteIncidentes'  # quitar 'dbo.'
        managed = False
