# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.core.context_processors import csrf
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import EditarPerfilForm
from personas.forms import PersonaForm

import datetime


class PerfilView(View):
    '''
    Clase para la renderización del Perfil
    '''
    template = 'perfil.html'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        mensaje = ''
        tipo = ''
        self.diccionario.update(csrf(request))
        usuario = request.user
        if not request.session.get('ultima_sesion', False):
            persistente = True
            mensaje = 'Recuerde cambiar su contraseña por seguridad...'
            tipo_mensaje = 'warning'
            self.diccionario.update({'tipo_mensaje':tipo_mensaje})
            self.diccionario.update({'mensaje':mensaje})
            request.session['ultima_sesion'] = datetime.datetime.today()

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            return HttpResponseRedirect(reverse('crear_perfil'))

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'mensaje':mensaje})
        self.diccionario.update({'tipo':tipo})

        # Revisamos si el usuario pertenece al grupo Operador
        # Y si pertenece, le cambiamos la plantilla y los filtros
        if usuario.groups.filter(name__iexact='operador').exists():
            aspirantes = listaAspirantes()
            auditores = Auditor.objects.filter(Q(estatus__nombre='Renovado')|Q(estatus__nombre='Inscrito'))
            self.template = 'perfil/perfil_operador.html'

            paginator = Paginator(auditores, settings.LIST_PER_PAGE)
            page = request.GET.get('page')
            try:
                auditores = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                auditores = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                auditores = paginator.page(paginator.num_pages)

            paginator = Paginator(aspirantes, settings.LIST_PER_PAGE)
            page = request.GET.get('page')
            try:
                aspirantes = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                aspirantes = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                aspirantes = paginator.page(paginator.num_pages)

            self.diccionario.update({'aspirantes':aspirantes})
            self.diccionario.update({'auditores':auditores})

        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class EditarPerfilView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='perfil/editar_formulario.html'
    persona_form = EditarPerfilForm
    titulo = 'información personal'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        try:
            request.user.get_profile()
        except:
            url = reverse('crear_persona')

        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        persona = Persona.objects.get(userprofile=usuario.profile)
        self.persona_form = self.persona_form(instance=persona)
        self.diccionario.update({'persona':persona})

        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.persona_form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.persona_form = PersonaForm(request.POST)

        self.diccionario.update(csrf(request))
        self.diccionario.update({'persona_form':self.persona_form})
        persona = request.user.get_profile().persona

        estado = Estado.objects.get(id=request.POST['reside'])
        fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 

        persona = Persona.objects.get(cedula=persona.cedula)
        persona.primer_nombre = request.POST['primer_nombre']
        persona.segundo_nombre = request.POST['segundo_nombre']
        persona.primer_apellido = request.POST['primer_apellido']
        persona.segundo_apellido = request.POST['segundo_apellido']
        persona.genero = request.POST['genero']
        persona.reside = estado
        persona.direccion = request.POST['direccion']
        persona.fecha_nacimiento = fecha_nacimiento
        persona.tlf_reside = request.POST['tlf_reside']
        persona.tlf_movil = request.POST['tlf_movil']
        persona.tlf_oficina = request.POST['tlf_oficina']
        persona.tlf_contacto = request.POST['tlf_contacto']
        persona.estado_civil = request.POST['estado_civil']

        request.user.first_name = request.POST['primer_nombre']
        request.user.last_name = request.POST['primer_apellido']
        request.user.email = persona.email
        request.user.save()

        return redirect(reverse('perfil'))


class CrearPerfilView(View):
    '''
    Clase para postulación de currículum
    '''
    template='formulario.html'
    persona_form = PersonaForm
    titulo = u'Completa tus datos'
    descripcion = 'Ingresa toda tu información personal, \
        así podremos completar la creación de tu cuenta'

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'persona_form': persona_form})
    diccionario.update({'titulo': titulo})
    diccionario.update({'descripcion': descripcion})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.diccionario.update({'curriculum':True})
        self.diccionario.update({'mensaje_error':''})
        self.diccionario.update({'form':self.persona_form()})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.persona_form = PersonaForm(request.POST)

        email2_error = ''
        error_general = ''
        error = False

        if not self.persona_form.is_valid():
            self.diccionario.update(csrf(request))
            self.diccionario.update({'curriculum':True})
            mensaje_error = ''
            if self.persona_form.errors.has_key('__all__'):
                mensaje_error = self.persona_form.errors['__all__'][0]
            self.diccionario.update({'mensaje_error':mensaje_error})
            self.diccionario.update({'form':self.persona_form})
            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )

        else:
            estado = Estado.objects.get(id=request.POST['reside'])
            fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            persona = Persona.objects.create( cedula=request.POST['cedula'],
                                              primer_nombre = request.POST['primer_nombre'],
                                              segundo_nombre = request.POST['segundo_nombre'],
                                              primer_apellido = request.POST['primer_apellido'],
                                              segundo_apellido = request.POST['segundo_apellido'],
                                              genero = request.POST['genero'],
                                              reside = estado,
                                              direccion = request.POST['direccion'],
                                              fecha_nacimiento = fecha_nacimiento,
                                              tlf_reside = request.POST['tlf_reside'],
                                              tlf_movil = request.POST['tlf_movil'],
                                              tlf_oficina = request.POST['tlf_oficina'],
                                              tlf_contacto = request.POST['tlf_contacto'],
                                              estado_civil = request.POST['estado_civil'],
                                              email = request.user.email,
                                             )

            usuario = User.objects.get(username=request.user.username)

            usuario.is_active = True
            usuario.first_name = request.POST['primer_nombre']
            usuario.last_name = request.POST['primer_apellido']
            usuario.save()

            perfil = UserProfile.objects.get(user=usuario)
            perfil.persona = persona
            perfil.save()

        self.template = 'perfil/perfil.html'
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )