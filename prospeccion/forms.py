from django import forms

from .models import Comprador, HistorialContacto, PlantillaMensaje, Producto


class CompradorForm(forms.ModelForm):
    class Meta:
        model = Comprador
        fields = [
            'nombre_empresa', 'pais', 'ciudad', 'sector',
            'email', 'telefono', 'linkedin_url', 'facebook_url', 'instagram_url', 'sitio_web',
            'fuente', 'estado',
            'productos_interes', 'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 4}),
            'productos_interes': forms.SelectMultiple(attrs={'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs['class'] = (css + ' form-check-input').strip()
            elif isinstance(field.widget, forms.Select) or isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs['class'] = (css + ' form-select').strip()
            else:
                field.widget.attrs['class'] = (css + ' form-control').strip()


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
        help_text='Columnas esperadas: nombre_empresa, pais, ciudad, sector, email, telefono, fuente',
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
