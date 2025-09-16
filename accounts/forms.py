from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Div
from crispy_forms.bootstrap import Field
from .models import CustomUser, UserProfile


class CustomLoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión personalizado
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}

        self.helper.layout = Layout(
            HTML('<div class="text-center mb-4">'),
            HTML('<i class="bi bi-bank2 display-4 text-primary mb-3"></i>'),
            HTML('<h3 class="fw-bold">Iniciar Sesión</h3>'),
            HTML('<p class="text-muted">Accede a tu cuenta del Banco Familiar</p>'),
            HTML('</div>'),

            Field('username', css_class='form-control-lg'),
            Field('password', css_class='form-control-lg'),

            HTML('<div class="d-grid gap-2 mt-4">'),
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),

            HTML('<div class="text-center mt-3">'),
            HTML(
                '<p class="mb-0">¿No tienes cuenta? <a href="{% url \'accounts:register\' %}" class="text-decoration-none">Regístrate aquí</a></p>'),
            HTML('</div>')
        )


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de registro personalizado
    """
    email = forms.EmailField(
        label='Email',
        required=True,
        help_text='Ingresa un email válido. Este será tu nombre de usuario.'
    )

    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        required=True
    )

    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        required=True
    )

    telefono = forms.CharField(
        label='Teléfono',
        required=False,
        help_text='Formato: +595981123456'
    )

    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    terms_accepted = forms.BooleanField(
        label='Acepto los términos y condiciones',
        required=True,
        error_messages={'required': 'Debes aceptar los términos y condiciones'}
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'password1',
                  'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}

        # Personalizar mensajes de ayuda
        self.fields[
            'username'].help_text = 'Nombre de usuario único. Puede contener letras, números y @/./+/-/_ únicamente.'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres. No puede ser similar a tu información personal.'
        self.fields['password2'].help_text = 'Ingresa la misma contraseña para verificación.'

        self.helper.layout = Layout(
            HTML('<div class="text-center mb-4">'),
            HTML('<i class="bi bi-person-plus display-4 text-primary mb-3"></i>'),
            HTML('<h3 class="fw-bold">Crear Cuenta</h3>'),
            HTML('<p class="text-muted">Únete al Banco Familiar Simulador</p>'),
            HTML('</div>'),

            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),

            Field('username', css_class='mb-3'),
            Field('email', css_class='mb-3'),

            Row(
                Column('telefono', css_class='form-group col-md-6 mb-3'),
                Column('fecha_nacimiento', css_class='form-group col-md-6 mb-3'),
            ),

            Field('password1', css_class='mb-3'),
            Field('password2', css_class='mb-3'),

            Field('terms_accepted', css_class='mb-4'),

            HTML('<div class="d-grid gap-2">'),
            Submit('submit', 'Crear Cuenta', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),

            HTML('<div class="text-center mt-3">'),
            HTML(
                '<p class="mb-0">¿Ya tienes cuenta? <a href="{% url \'accounts:login\' %}" class="text-decoration-none">Inicia sesión</a></p>'),
            HTML('</div>')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = CustomUser.UserRole.CLIENTE  # Por defecto, los registros son clientes

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario
    """

    class Meta:
        model = UserProfile
        fields = [
            'cedula', 'profesion', 'ingresos_mensuales',
            'notificaciones_email', 'notificaciones_sms'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'

        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="bi bi-person-gear me-2"></i>Información del Perfil</h4>'),

            Row(
                Column('cedula', css_class='form-group col-md-6 mb-3'),
                Column('profesion', css_class='form-group col-md-6 mb-3'),
            ),

            Field('ingresos_mensuales', css_class='mb-3'),

            HTML('<h5 class="mt-4 mb-3">Configuraciones de Notificaciones</h5>'),
            Field('notificaciones_email', css_class='mb-2'),
            Field('notificaciones_sms', css_class='mb-4'),

            HTML('<div class="d-grid gap-2">'),
            Submit('submit', 'Actualizar Perfil', css_class='btn btn-primary'),
            HTML('</div>')
        )


class UserUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar información básica del usuario
    """

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'telefono', 'direccion', 'fecha_nacimiento']

    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'

        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="bi bi-person-circle me-2"></i>Información Personal</h4>'),

            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),

            Row(
                Column('telefono', css_class='form-group col-md-6 mb-3'),
                Column('fecha_nacimiento', css_class='form-group col-md-6 mb-3'),
            ),

            Field('direccion', css_class='mb-4'),

            HTML('<div class="d-grid gap-2">'),
            Submit('submit', 'Actualizar Información', css_class='btn btn-primary'),
            HTML('</div>')
        )