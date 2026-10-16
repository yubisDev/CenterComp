from django import forms
from django.urls import reverse
from django.utils.html import format_html

from .models import CategoriaInteres, Comprador, HistorialContacto, HistorialContactoProveedor, PlantillaMensaje, Producto, Proveedor


class CompradorForm(forms.ModelForm):
    class Meta:
        model = Comprador
        fields = [
            'nombre_contacto', 'nombre_empresa', 'pais', 'ciudad', 'sector',
            'email', 'telefono', 'whatsapp', 'linkedin_url', 'facebook_url', 'instagram_url', 'sitio_web',
            'fuente', 'campana', 'estado',
            'categorias_interes', 'acepta_mensajes',
            'productos_interes', 'palabras_clave_interes', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 4}),
            'productos_interes': forms.SelectMultiple(attrs={'size': 6}),
            'categorias_interes': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorias_interes'].queryset = CategoriaInteres.objects.filter(activa=True)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = (css + ' form-check-input').strip()
            elif isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs['class'] = (css + ' form-check-input').strip()
            elif isinstance(field.widget, forms.Select) or isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs['class'] = (css + ' form-select').strip()
            else:
                field.widget.attrs['class'] = (css + ' form-control').strip()

    def clean(self):
        datos = super().clean()
        if not (datos.get('nombre_empresa') or '').strip() and not (datos.get('nombre_contacto') or '').strip():
            raise forms.ValidationError('Escribe al menos el nombre de contacto o el de la empresa.')

        numero = datos.get('telefono') or datos.get('whatsapp')
        if numero:
            from .normalizacion import normalizar_telefono
            normalizado = normalizar_telefono(numero, datos.get('pais', ''))
            otro = Comprador.objects.filter(telefono_normalizado=normalizado).exclude(pk=self.instance.pk).first()
            if normalizado and otro:
                self.add_error('telefono', format_html(
                    'Este número ya está registrado en <a href="{}">{}</a>. Edita ese registro en lugar de crear otro.',
                    reverse('comprador_detalle', args=[otro.pk]), otro.nombre_mostrar,
                ))
        return datos


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'descripcion', 'cantidad_disponible',
            'precio_referencia', 'valor_estimado', 'condiciones_venta',
            'referencia', 'confidencial',
            'proveedor_nombre', 'proveedor_contacto', 'proveedor_email', 'proveedor_telefono',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'condiciones_venta': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class PlantillaMensajeForm(forms.ModelForm):
    class Meta:
        model = PlantillaMensaje
        fields = ['nombre', 'tipo', 'asunto', 'cuerpo']
        widgets = {
            'cuerpo': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'tipo':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class HistorialContactoForm(forms.ModelForm):
    class Meta:
        model = HistorialContacto
        fields = ['medio', 'resultado']
        widgets = {
            'resultado': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medio'].widget.attrs['class'] = 'form-select'
        self.fields['resultado'].widget.attrs['class'] = 'form-control'


class ImportarCompradoresForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo CSV o Excel',
        help_text='Excel (.xlsx) o CSV. También sirve el CSV que descarga Meta Lead Ads.',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv,.tsv,.txt,.xlsx'}),
    )
    fuente = forms.ChoiceField(
        label='Origen (si el archivo no lo trae)', required=False,
        choices=[('', 'Detectar automáticamente')] + list(Comprador.Fuente.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Ej. "WhatsApp" si son contactos exportados del WhatsApp Business.',
    )
    campana = forms.CharField(
        label='Campaña (si el archivo no la trae)', required=False, max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Revestimientos Panamá - octubre'}),
    )
    categorias = forms.ModelMultipleChoiceField(
        label='Asignar a todos estas categorías', required=False,
        queryset=CategoriaInteres.objects.filter(activa=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Además de las que se detecten en el archivo. Útil si exportaste una etiqueta de WhatsApp.',
    )
    acepta_mensajes = forms.BooleanField(
        label='Todos aceptaron recibir promociones', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre_empresa', 'pais', 'ciudad', 'sector',
            'email', 'telefono', 'whatsapp', 'linkedin_url', 'facebook_url', 'instagram_url', 'sitio_web',
            'fuente', 'estado', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = (css + ' form-select').strip()
            else:
                field.widget.attrs['class'] = (css + ' form-control').strip()


class HistorialContactoProveedorForm(forms.ModelForm):
    class Meta:
        model = HistorialContactoProveedor
        fields = ['medio', 'resultado']
        widgets = {
            'resultado': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medio'].widget.attrs['class'] = 'form-select'
        self.fields['resultado'].widget.attrs['class'] = 'form-control'


class ImportarProductosForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo CSV o Excel',
        help_text='Obligatoria: nombre. Opcionales: categoria, descripcion, cantidad_disponible, precio_referencia, '
                   'valor_estimado, condiciones_venta, referencia, confidencial, proveedor_nombre, '
                   'proveedor_contacto, proveedor_email, proveedor_telefono',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'}),
    )


class BusquedaIAForm(forms.Form):
    consulta = forms.CharField(
        label='¿Qué empresas buscamos?',
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. empresas de electrónica en México',
        }),
    )
