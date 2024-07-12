from django.db import models
import jsonfield

# Create your models here.

class cpPais(models.Model):
    CP = models.CharField(max_length=10, primary_key=True)
    Localidad = models.CharField(max_length=100)
    Partido = models.CharField(max_length=100)
    Provincia = models.CharField(max_length=100)
    REGION = models.CharField(max_length=100)
    DISTRITO = models.CharField(max_length=100)
    ZONA = models.CharField(max_length=100)
    AMBA_INTRALOG = models.CharField(max_length=100)
    ZONA_FLEX = models.CharField(max_length=100)
    FLEX_INTRA = models.CharField(max_length=100)
    RANGO_CP = models.CharField(max_length=100)
    CPA = models.CharField(max_length=100)


class bdoms(models.Model):
    pedido = models.CharField(max_length=50, null=True)
    flujo = models.CharField(max_length=2, null=True)
    seller = models.CharField(max_length=50, null=True)
    sucCodigo = models.CharField(max_length=100, null=True)
    estadoPedido = models.CharField(max_length=30, null=True)
    fechaCreacion = models.DateTimeField(null=True)
    fechaRecepcion = models.DateTimeField(null=True)
    fechaDespacho = models.DateTimeField(null=True)
    fechaEntrega = models.DateTimeField(null=True)
    lpn = models.CharField(max_length=100, primary_key=True)
    estadoLpn = models.CharField(max_length=50, null=True)
    zona = models.CharField(max_length=10, null=True)
    trackingDistribucion = models.CharField(max_length=50, null=True)
    trackingTransporte = models.CharField(max_length=50, null=True)
    tipo = models.CharField(max_length=6, null=True)
    codigoPostal = models.ForeignKey(cpPais, on_delete=models.CASCADE)
    tte = models.CharField(max_length=50, null=True)
    tteSucursalDistribucion = models.CharField(max_length=3, null=True)
    tiendaEntrega = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Order {self.pedido} Piece {self.lpn}"


class TrackingEventCA(models.Model):
    tracking_number = models.CharField(max_length=255, unique=True)
    raw_data = jsonfield.JSONField()  # Add this field to store the raw event data

    def __str__(self):
        return self.tracking_number

class EventDetail(models.Model):
    tracking_event = models.ForeignKey(TrackingEventCA, related_name='events', on_delete=models.CASCADE)
    facility_code = models.CharField(max_length=50)
    status_id = models.CharField(max_length=50)
    status = models.CharField(max_length=100)
    date = models.DateTimeField()
    sign = models.CharField(max_length=100, blank=True, null=True)
    facility = models.CharField(max_length=100)

    def __str__(self):
        return f"Event at {self.facility} with status {self.status}"

class OrderTracking(models.Model):
    pedido = models.CharField(max_length=50)
    tracking_event = models.ForeignKey(TrackingEventCA, related_name='order_trackings', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pedido', 'tracking_event')

    def __str__(self):
        return f"Order {self.pedido} - Tracking {self.tracking_event.tracking_number}"
    
    class ProcessingState(models.Model):
        key = models.CharField(max_length=255, unique=True)
        value = models.CharField(max_length=255)

        def __str__(self):
            return f"{self.key}: {self.value}"