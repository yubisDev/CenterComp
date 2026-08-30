from django.conf import settings
from django.db import models
from django.urls import reverse


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField(blank=True)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    precio_referencia = models.DecimalField(
        'Precio de venta (referencia)', max_digits=14, decimal_places=2, null=True, blank=True,
    )
    valor_estimado = models.DecimalField(
        'Valor bruto estimado', max_digits=14, decimal_places=2, null=True, blank=True,
        help_text='Valuación/tasación del lote, si es distinta al precio de venta (ej. avalúo antes de descuento).',
    )
    condiciones_venta = models.TextField(
        'Condiciones / escenarios de venta', blank=True,
        help_text='Ej. venta en bloque, venta por categorías, colateral financiero — con sus montos y plazos.',
    )
    referencia = models.CharField(
        'Referencia interna', max_length=100, blank=True,
        help_text='Código del documento de origen, ej. H11-INV-RCA-001.',
    )
    confidencial = models.BooleanField(
        default=False,
        help_text='Marca este lote como confidencial (documento de origen restringido a su destinatario).',
    )

    proveedor_nombre = models.CharField('Proveedor / consignante', max_length=200, blank=True)
    proveedor_contacto = models.CharField('Persona de contacto', max_length=150, blank=True)
    proveedor_email = models.EmailField('Correo del proveedor', blank=True)
    proveedor_telefono = models.CharField('Teléfono del proveedor', max_length=30, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Comprador(models.Model):
    class Estado(models.TextChoices):
        POR_CONTACTAR = 'por_contactar', 'Por contactar'
        CONTACTADO = 'contactado', 'Contactado'
        INTERESADO = 'interesado', 'Interesado'
        DESCARTADO = 'descartado', 'Descartado'
        CLIENTE = 'cliente', 'Cliente'

    class Fuente(models.TextChoices):
        HUNTER = 'hunter', 'Hunter.io'
        APOLLO = 'apollo', 'Apollo'
        PROCOLOMBIA = 'procolombia', 'Procolombia'
        CAMARA_COMERCIO = 'camara_comercio', 'Cámara de comercio'
        LINKEDIN = 'linkedin', 'LinkedIn Sales Navigator'
        IA = 'ia', 'Búsqueda con IA'
        FACEBOOK_ADS = 'facebook_ads', 'Facebook Ads'
        INSTAGRAM_ADS = 'instagram_ads', 'Instagram Ads'
        MANUAL = 'manual', 'Manual'
        OTRO = 'otro', 'Otro'

    nombre_empresa = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100, blank=True)
    sector = models.CharField(max_length=120, blank=True)

    email = models.EmailField(blank=True)
    telefono = models.CharField(
        'Teléfono / WhatsApp', max_length=30, blank=True,
        help_text='Incluir indicativo de país, ej: +57 300 1234567',
    )
    linkedin_url = models.URLField('LinkedIn', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    sitio_web = models.URLField('Sitio web', blank=True)

    fuente = models.CharField(max_length=30, choices=Fuente.choices, default=Fuente.MANUAL)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.POR_CONTACTAR)

    productos_interes = models.ManyToManyField(Producto, blank=True, related_name='compradores_interesados')

    notas = models.TextField('Notas de seguimiento', blank=True)
    fecha_ultimo_contacto = models.DateTimeField(null=True, blank=True)

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='compradores_asignados',
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['pais']),
            models.Index(fields=['sector']),
            models.Index(fields=['fuente']),
        ]

    def __str__(self):
        return f'{self.nombre_empresa} ({self.pais})'

    def get_absolute_url(self):
        return reverse('comprador_detalle', args=[self.pk])

    @property
    def whatsapp_numero(self):
        return ''.join(ch for ch in self.telefono if ch.isdigit())


class HistorialContacto(models.Model):
    class Medio(models.TextChoices):
        EMAIL = 'email', 'Correo'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEFONO = 'telefono', 'Teléfono'
        REUNION = 'reunion', 'Reunión'
        OTRO = 'otro', 'Otro'

    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name='historial')
    fecha = models.DateTimeField(auto_now_add=True)
    medio = models.CharField(max_length=20, choices=Medio.choices, default=Medio.EMAIL)
    resultado = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de contacto'
        verbose_name_plural = 'Historial de contactos'

    def __str__(self):
        return f'{self.comprador} - {self.get_medio_display()} - {self.fecha:%Y-%m-%d}'


class PlantillaMensaje(models.Model):
    class Tipo(models.TextChoices):
        EMAIL = 'email', 'Correo'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.EMAIL)
    asunto = models.CharField(max_length=200, blank=True, help_text='Solo aplica para plantillas de correo')
    cuerpo = models.TextField(
        help_text='Usa variables como {nombre_empresa} y {producto} para personalizar el mensaje',
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'

    def render(self, comprador, producto_nombre=''):
        class _ContextoSeguro(dict):
            def __missing__(self, key):
                return ''

        contexto = _ContextoSeguro(
            nombre_empresa=comprador.nombre_empresa,
            pais=comprador.pais,
            ciudad=comprador.ciudad,
            sector=comprador.sector,
            producto=producto_nombre,
        )
        asunto = self.asunto.format_map(contexto) if self.asunto else ''
        cuerpo = self.cuerpo.format_map(contexto)
        return asunto, cuerpo


class BusquedaIA(models.Model):
    """Bitácora de cada búsqueda con IA — solo para poder contar cuántas se
    hicieron hoy y frenar antes de acercarse a la cuota/gasto configurado."""

    consulta = models.CharField(max_length=300)
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    resultados = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Búsqueda con IA'
        verbose_name_plural = 'Búsquedas con IA'

    def __str__(self):
        return f'{self.consulta} ({self.creado_en:%Y-%m-%d %H:%M})'
