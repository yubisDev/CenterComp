from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .normalizacion import normalizar_pais, normalizar_telefono, pais_desde_telefono


class CategoriaInteres(models.Model):
    """Línea de negocio que le interesa a un lead (vehículos de subasta,
    inmuebles, revestimientos...). Es un modelo y no una lista fija para que
    se puedan agregar categorías nuevas desde el admin sin programar."""

    nombre = models.CharField(max_length=100, unique=True)
    palabras_clave = models.CharField(
        max_length=400, blank=True,
        help_text='Separadas por coma. Al importar, si la columna de interés contiene alguna de estas '
                  'palabras, se asigna esta categoría. Ej: "carro, vehiculo, camioneta, moto".',
    )
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría de interés'
        verbose_name_plural = 'Categorías de interés'

    def __str__(self):
        return self.nombre

    def lista_palabras(self):
        return [p.strip() for p in self.palabras_clave.split(',') if p.strip()]


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
        META_ADS = 'meta_ads', 'Anuncio de Meta (formulario)'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        INSTAGRAM = 'instagram', 'Instagram (mensaje directo)'
        PAGINA_WEB = 'pagina_web', 'Página web'
        MANUAL = 'manual', 'Manual'
        OTRO = 'otro', 'Otro'

    nombre_empresa = models.CharField('Empresa', max_length=200, blank=True)
    nombre_contacto = models.CharField(
        'Nombre de contacto', max_length=150, blank=True,
        help_text='Persona que escribió o con quien se habla. Se exige empresa o nombre de contacto.',
    )
    pais = models.CharField(
        max_length=100, blank=True,
        help_text='Si se deja vacío, se deduce del indicativo del teléfono.',
    )
    ciudad = models.CharField(max_length=100, blank=True)
    sector = models.CharField(max_length=120, blank=True)

    email = models.EmailField(blank=True)
    telefono = models.CharField(
        'Teléfono / WhatsApp', max_length=30, blank=True,
        help_text='Incluir indicativo de país, ej: +57 300 1234567',
    )
    whatsapp = models.CharField(
        'WhatsApp', max_length=30, blank=True,
        help_text='Solo si es distinto del teléfono. Con indicativo, ej: +62 812 3456 7890',
    )
    linkedin_url = models.URLField('LinkedIn', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    sitio_web = models.URLField('Sitio web', blank=True)

    telefono_normalizado = models.CharField(
        max_length=20, blank=True, editable=False, db_index=True,
        help_text='Número con indicativo y solo dígitos; se calcula solo. Sirve para detectar duplicados.',
    )

    fuente = models.CharField(max_length=30, choices=Fuente.choices, default=Fuente.MANUAL)
    campana = models.CharField(
        'Campaña / anuncio', max_length=200, blank=True,
        help_text='De qué anuncio o campaña llegó. Ej: "Revestimientos Panamá - septiembre".',
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.POR_CONTACTAR)

    categorias_interes = models.ManyToManyField(
        CategoriaInteres, blank=True, related_name='compradores', verbose_name='Categorías de interés',
    )
    acepta_mensajes = models.BooleanField(
        'Acepta recibir promociones', default=False,
        help_text='Marcar solo si la persona aceptó recibir mensajes promocionales (WhatsApp o correo). '
                  'Meta lo exige para envíos masivos.',
    )
    fecha_acepta = models.DateTimeField(null=True, blank=True, editable=False)

    productos_interes = models.ManyToManyField(Producto, blank=True, related_name='compradores_interesados')

    palabras_clave_interes = models.CharField(
        'Palabras clave de interés', max_length=300, blank=True,
        help_text='Separadas por coma. Ej: "chatarra, motor cummins, vehiculos pesados". '
                   'Cuando entre un producto nuevo que coincida, se le avisa a este comprador automáticamente.',
    )

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
        return f'{self.nombre_mostrar} ({self.pais})' if self.pais else self.nombre_mostrar

    def get_absolute_url(self):
        return reverse('comprador_detalle', args=[self.pk])

    @property
    def nombre_mostrar(self):
        """Empresa si la hay; si no, el nombre de la persona."""
        return self.nombre_empresa or self.nombre_contacto or '(sin nombre)'

    @property
    def nombre_saludo(self):
        """Para saludar en un mensaje: la persona si la conocemos, si no la empresa."""
        return self.nombre_contacto or self.nombre_empresa

    @property
    def whatsapp_numero(self):
        numero = self.whatsapp or self.telefono
        return normalizar_telefono(numero, self.pais) if numero else ''

    def save(self, *args, **kwargs):
        self.pais = normalizar_pais(self.pais)
        numero = self.telefono or self.whatsapp
        self.telefono_normalizado = normalizar_telefono(numero, self.pais) if numero else ''
        if not self.pais and numero:
            self.pais = pais_desde_telefono(numero)
        if self.acepta_mensajes and not self.fecha_acepta:
            self.fecha_acepta = timezone.now()
        elif not self.acepta_mensajes:
            self.fecha_acepta = None
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {'pais', 'telefono_normalizado', 'fecha_acepta'}
        super().save(*args, **kwargs)


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


class Proveedor(models.Model):
    """Empresas o personas que le dan inventario a ISYN para vender/subastar
    (consignantes) — el lado opuesto de Comprador. Incluye chatarreros que
    llegan directo y empresas encontradas con la búsqueda con IA."""

    class Estado(models.TextChoices):
        POR_CONTACTAR = 'por_contactar', 'Por contactar'
        CONTACTADO = 'contactado', 'Contactado'
        NEGOCIANDO = 'negociando', 'Negociando'
        CONSIGNO = 'consigno', 'Consignó inventario'
        DESCARTADO = 'descartado', 'Descartado'

    class Fuente(models.TextChoices):
        CHATARREO = 'chatarreo', 'Chatarreo'
        IA = 'ia', 'Búsqueda con IA'
        MANUAL = 'manual', 'Manual'
        OTRO = 'otro', 'Otro'

    nombre_empresa = models.CharField(max_length=200)
    pais = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    sector = models.CharField(max_length=120, blank=True)

    email = models.EmailField(blank=True)
    telefono = models.CharField(
        'Teléfono / WhatsApp', max_length=30, blank=True,
        help_text='Incluir indicativo de país, ej: +57 300 1234567',
    )
    whatsapp = models.CharField(
        'WhatsApp', max_length=30, blank=True,
        help_text='Solo si es distinto del teléfono. Con indicativo, ej: +62 812 3456 7890',
    )
    linkedin_url = models.URLField('LinkedIn', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    sitio_web = models.URLField('Sitio web', blank=True)

    fuente = models.CharField(max_length=30, choices=Fuente.choices, default=Fuente.MANUAL)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.POR_CONTACTAR)

    notas = models.TextField('Notas de seguimiento', blank=True)
    fecha_ultimo_contacto = models.DateTimeField(null=True, blank=True)

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='proveedores_asignados',
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
        return f'{self.nombre_empresa} ({self.pais})' if self.pais else self.nombre_empresa

    def get_absolute_url(self):
        return reverse('proveedor_detalle', args=[self.pk])

    @property
    def whatsapp_numero(self):
        return ''.join(ch for ch in (self.whatsapp or self.telefono) if ch.isdigit())


class HistorialContactoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='historial')
    fecha = models.DateTimeField(auto_now_add=True)
    medio = models.CharField(max_length=20, choices=HistorialContacto.Medio.choices, default=HistorialContacto.Medio.EMAIL)
    resultado = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de contacto (proveedor)'
        verbose_name_plural = 'Historial de contactos (proveedores)'

    def __str__(self):
        return f'{self.proveedor} - {self.get_medio_display()} - {self.fecha:%Y-%m-%d}'


class PlantillaMensaje(models.Model):
    class Tipo(models.TextChoices):
        EMAIL = 'email', 'Correo'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.EMAIL)
    asunto = models.CharField(max_length=200, blank=True, help_text='Solo aplica para plantillas de correo')
    cuerpo = models.TextField(
        help_text='Variables disponibles: {nombre} (persona o empresa), {nombre_empresa}, {categoria}, '
                  '{producto}, {pais} y {ciudad}.',
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'

    def render(self, comprador, producto_nombre=''):
        class _ContextoSeguro(dict):
            def __missing__(self, key):
                return ''

        categorias = ''
        if comprador.pk:
            categorias = ', '.join(c.nombre for c in comprador.categorias_interes.all())
        contexto = _ContextoSeguro(
            nombre_empresa=comprador.nombre_empresa or comprador.nombre_contacto,
            nombre=comprador.nombre_saludo,
            categoria=categorias,
            pais=comprador.pais,
            ciudad=comprador.ciudad,
            sector=comprador.sector,
            producto=producto_nombre,
        )
        asunto = self.asunto.format_map(contexto) if self.asunto else ''
        cuerpo = self.cuerpo.format_map(contexto)
        return asunto, cuerpo


class BusquedaIA(models.Model):
    """Bitácora de cada búsqueda con IA — cuenta cuántas se hicieron hoy para
    frenar antes de acercarse a la cuota/gasto configurado, y además hace de
    "trabajo en segundo plano": la búsqueda real corre en un hilo aparte y
    va actualizando este mismo registro, para que la pantalla no se quede
    congelada esperando la respuesta de la IA."""

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Procesando'
        LISTO = 'listo', 'Listo'
        ERROR = 'error', 'Error'

    class Tipo(models.TextChoices):
        COMPRADOR = 'comprador', 'Buscar compradores'
        PROVEEDOR = 'proveedor', 'Buscar proveedores/consignantes'

    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.COMPRADOR)
    consulta = models.CharField(max_length=300)
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    resultados = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    resultados_json = models.JSONField(null=True, blank=True)
    fuentes_json = models.JSONField(null=True, blank=True)
    error_mensaje = models.TextField(blank=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Búsqueda con IA'
        verbose_name_plural = 'Búsquedas con IA'

    def __str__(self):
        return f'{self.consulta} ({self.creado_en:%Y-%m-%d %H:%M})'
