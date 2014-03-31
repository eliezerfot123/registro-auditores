# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.db.models import Q

from curriculum.models import *
from curriculum.forms import *
from personas.models import *
from personas.forms import *
from auth.models import *
import datetime


def aptitudes(request):
    '''
    Revisión de cada una de las aptitudes de la persona
    '''
    listado = []

    laborales = Laboral.objects.filter(
            usuario=request.user.profile)
    educaciones = Educacion.objects.filter(
            persona=request.user.profile.persona)
    conocimientos = Conocimiento.objects.filter(
            usuario=request.user.profile)
    competencias = Competencia.objects.filter(
            usuario=request.user.profile)
    habilidades = Habilidad.objects.filter(
            usuario=request.user.profile)
    idiomas = Idioma.objects.filter(
            persona=request.user.profile.persona)

    listado.append(laborales)
    listado.append(educaciones)
    listado.append(conocimientos)
    listado.append(competencias)
    listado.append(habilidades)
    listado.append(idiomas)

    return listado


def lista_filtros(request):
    '''
    Envío de variables con las aptitudes ya filtradas
    '''
    listado = aptitudes(request)
    requisitos = revisar_requisitos(listado)

    listado = {'laborales': listado[0],
                'educaciones': listado[1],
                'conocimientos': listado[2],
                'competencias': listado[3],
                'habilidades': listado[4],
                'idiomas': listado[5],
                'requisitos': requisitos,
                }

    return listado


def revisar_requisitos(listado):
    '''
    Validar si todos los requisitos se satisfacen
    para proceder a la fijación de fecha para la cita.
    Retorna True si la información es suficiente.
    Retorna False si falta información.
    '''
    for lista in listado:
        if not lista.exists():
            return False
    return True


class CitasView(View):
    '''
    Clase para la renderización de las citas
    '''
    template = 'perfil/editar_formulario.html'
    citas_form = CitasForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'citas'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        listado = aptitudes(request)
        requisitos = revisar_requisitos(listado)
        usuario = request.user
        self.diccionario.update(csrf(request))
        nueva = True
        if requisitos:
            self.tipo_mensaje = 'info'
            self.mensaje = 'Debe seleccionar tres fechas tentativas en las '
            self.mensaje += 'que desearía tener una cita con nosotros.'
            cita = Cita.objects.filter(usuario = usuario.profile)
            if cita.exists():
                self.citas_form = self.citas_form(instance = cita[0])

        else:
            self.template = 'perfil/perfil.html'
            self.tipo_mensaje = 'warning'
            self.mensaje = u'Debe tener toda la información '
            self.mensaje += u'curricular completa. Por favor, revísela.'
        self.diccionario.update({'persona': usuario.profile.persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.citas_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        listado = aptitudes(request)
        requisitos = revisar_requisitos(listado)
        usuario = request.user
        self.diccionario.update(csrf(request))
        nueva = True
        if not requisitos:
            self.template = 'perfil/perfil.html'
            self.tipo_mensaje = 'warning'
            self.mensaje = u'Debe tener toda la información '
            self.mensaje += u'curricular completa. Por favor, revísela.'
        else:
            self.diccionario.update(csrf(request))
            self.citas_form = self.citas_form(request.POST)
            usuario = request.user
            nueva = True
            fecha_1 = datetime.datetime.strptime(
                    request.POST['primera_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_2 = datetime.datetime.strptime(
                    request.POST['segunda_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_3 = datetime.datetime.strptime(
                    request.POST['tercera_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")

            if self.citas_form.is_valid():
                if nueva:
                    cita = Cita.objects.filter(usuario = usuario.profile)
                    if cita.exists():
                        cita = cita[0]
                        cita.primera_fecha = primera_fecha = fecha_1
                        cita.segunda_fecha = segunda_fecha = fecha_2
                        cita.tercera_fecha = tercera_fecha = fecha_3
                        cita.save()
                    else:
                        cita = Cita.objects.create(usuario = usuario.profile,
                                primera_fecha = fecha_1,
                                segunda_fecha = fecha_2,
                                tercera_fecha = fecha_3)

                    self.mensaje = "Las fechas para cita ha sido cargada con "
                    self.mensaje += "éxito. Se ha enviado su información a "
                    self.mensaje += "los administradores"
                    self.tipo_mensaje = 'success'
                    self.template = 'perfil/perfil.html'
            else:
                if self.citas_form.errors:
                    self.mensaje = self.citas_form.errors['__all__'][0]
                    self.tipo_mensaje = 'error'
        self.diccionario.update({'persona':usuario.profile.persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.citas_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class EducacionView(View):
    '''
    Clase para la renderización de los datos educativos
    '''
    template='perfil/editar_formulario.html'
    educacion_form = EducacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'educacion'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.educacion_form()})
        if kwargs.has_key('educacion_id') and not kwargs['educacion_id'] == None:
            nueva = False
            try:
                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            except:
                raise Http404

            if educacion.persona == usuario.userprofile_set.get_query_set()[0].persona:
                self.educacion_form = self.educacion_form(instance=educacion)
            else:
                raise PermissionDenied

        # Si se elimina una Educación
        if kwargs['palabra'] == 'eliminar':
            educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            educacion.delete()

            self.mensaje = u'Información educacional ha sido eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.educacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        guardado = False

        persona = request.user.userprofile_set.get_query_set()[0].persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            institucion = Institucion.objects.get(id=request.POST['institucion'])
            tipo = TipoEducacion.objects.get(id=request.POST['tipo'])
            fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            titulo = request.POST['titulo']

            if kwargs['palabra'] == 'editar':
                # Si se edita una Educación
                # Búsqueda de variables con los IDs enviados por POST
                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
                educacion.institucion = institucion
                educacion.tipo = tipo
                educacion.fecha_inicio = fecha_inicio
                educacion.fecha_fin = fecha_fin
                educacion.titulo = titulo

                educacion.save()

                self.mensaje = u'Información educacional ha sido editada exitosamente'
                self.tipo_mensaje = u'success'
            else:
                # Si se crea una Educación
                educacion = Educacion.objects.create(persona=persona, institucion=institucion, tipo=tipo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, titulo=titulo)
                self.mensaje = u'Información educacional ha sido creada exitosamente'
                self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.educacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class CurriculumView(View):
    '''
    Clase para postulación de currículum
    '''
    template='curriculum/postulacion.html'
    persona_form = PersonaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'persona_form':persona_form})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('inicio')
        self.diccionario.update(csrf(request))
        self.diccionario.update({'curriculum':True})
        self.diccionario.update({'form':self.persona_form()})
        mensaje_error = ''
        self.diccionario.update({'mensaje_error':mensaje_error})
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
            persona = Persona.objects.create(cedula=request.POST['cedula'],
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
                                             email = request.POST['email'],
                                             )

            # Se crea el usuario con el correo electrónico por defecto y se crea una contraseña aleatoria para el usuario
            clave = User.objects.make_random_password()
            usuario = User.objects.create_user(username = request.POST['email'],
                                              email = request.POST['email'], 
                                              first_name = request.POST['primer_nombre'],
                                              last_name = request.POST['segundo_nombre'],
                                              password = clave, 
                                             )

            usuario.is_active = True
            usuario.first_name = request.POST['primer_nombre']
            usuario.last_name = request.POST['primer_apellido']
            usuario.save()

            usuario_perfil = UserProfile.objects.create(persona=persona, user=usuario)

            # Envío de mail
            asunto = u'[SUSCERTE] Creación de cuenta exitosa'
            mensaje = Mensaje.objects.get(caso='Creación de usuario (email)')
            emisor = settings.EMAIL_HOST_USER
            destinatarios = (request.POST['email'],)

            # Sustitución de variables clave y usuario
            mensaje = mensaje.mensaje.replace('<clave>','%s'%(clave)).replace('<cuenta>','%s'%(request.POST['email']))
            send_mail(subject=asunto, message=mensaje, from_email=emisor, recipient_list=destinatarios)

        self.template = 'curriculum/aprobados.html'
        mensaje = Mensaje.objects.get(caso='Creación de usuario (web)')
        mensaje = mensaje.mensaje
        self.diccionario.update({'mensaje':mensaje})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class PerfilView(View):
    '''
    Clase para la renderización del Perfil
    '''
    template = 'perfil/perfil.html'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        mensaje = ''
        tipo = ''
        self.diccionario.update(csrf(request))
        usuario = request.user
        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'mensaje':mensaje})
        self.diccionario.update({'tipo':tipo})

        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class EditarPersonaView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='perfil/editar_formulario.html'
    persona_form = EditarPersonaForm
    titulo = 'información personal'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.persona_form = self.persona_form(instance=persona)

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.persona_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = Persona.objects.get(id=usuario.profile.persona.id)
        estado = Estado.objects.get(id=request.POST['reside'])
        fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 

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
        persona.save()

        self.mensaje = u'Información personal editada exitosamente'
        self.tipo_mensaje = u'success'

        self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.persona_form})

        self.lista_filtros = lista_filtros(request.user.profile.persona)
        self.diccionario.update(self.lista_filtros)

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class LaboralView(View):
    '''
    Clase para la renderización de los datos laborales
    '''
    template='perfil/editar_formulario.html'
    laboral_form = LaboralForm 
    titulo = 'laboral'
    mensaje = ''
    tipo_mensaje = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})
    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.laboral_form()})

        # Si se elimina una Educación
        if kwargs.has_key('laboral_id') and not kwargs['laboral_id'] == None:
            nueva = False
            try:
                laboral = Laboral.objects.get(id=int(kwargs['laboral_id']))
            except:
                raise Http404

            # Si el usuario de laboral no es el mismo al loggeado, retornar permisos denegados
            if laboral.usuario == usuario.profile:
                self.laboral_form = self.laboral_form(instance=laboral)
            else:
                raise PermissionDenied
        else:
            self.laborales = Laboral.objects.filter(usuario=request.user.profile)

        if kwargs['palabra'] == 'eliminar':
            educacion = Laboral.objects.get(id=int(kwargs['laboral_id']))
            educacion.delete()

            self.mensaje = u'Información laboral ha sido eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'formulario':self.laboral_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.laboral_form = self.laboral_form(request.POST)
        usuario = request.user
        guardado = False

        usuario = usuario.profile
        empresa = request.POST['empresa']
        sector = request.POST['sector']
        estado = Estado.objects.get(id=request.POST['estado'])
        telefono = request.POST['telefono']
        cargo = request.POST['cargo']
        funcion = request.POST['funcion']
        fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
        fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 
        retiro = request.POST['retiro']
        direccion_empresa = request.POST['direccion_empresa']
        trabajo_actual = False

        if self.laboral_form.is_valid():
            if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
                if kwargs['palabra'] == 'editar':
                    # Si se edita información laboral 
                    # Búsqueda de variables con los IDs enviados por POST
                    
                    laboral = laboral.objects.get(id=kwargs['laboral_id'])
                    laboral.empresa = empresa
                    laboral.sector = sector
                    laboral.estado = estado
                    laboral.telefono = telefono
                    laboral.cargo = cargo
                    laboral.funcion = funcion
                    laboral.fecha_inicio = fecha_inicio
                    laboral.fecha_fin = fecha_fin
                    laboral.retiro = retiro
                    laboral.direccion_empresa = direccion_empresa
                    laboral.trabajo_actual = trabajo_actual

                    laboral.save()

                    self.mensaje = u'Información laboral ha sido editada exitosamente'
                    self.tipo_mensaje = u'success'

                else:
                    # Si se crea información laboral 
                    laboral = Laboral.objects.create(usuario = usuario, empresa=empresa, sector=sector, estado=estado, telefono=telefono, cargo=cargo, funcion=funcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, retiro=retiro, direccion_empresa=direccion_empresa, trabajo_actual=trabajo_actual)
                    self.mensaje = u'Información laboral ha sido creada exitosamente'
                    self.tipo_mensaje = u'success'



            self.template = 'perfil/perfil.html'

        else:
            if self.laboral_form.errors.has_key('__all__'):
                self.tipo_mensaje = 'error'
                self.mensaje = self.laboral_form.errors['__all__'][0]
                laboral = laboral.objects.get(id=kwargs['laboral_id'])
                laboral.empresa = empresa
                laboral.sector = sector
                laboral.estado = estado
                laboral.telefono = telefono
                laboral.cargo = cargo
                laboral.funcion = funcion
                laboral.fecha_inicio = fecha_inicio
                laboral.fecha_fin = fecha_fin
                laboral.retiro = retiro
                laboral.direccion_empresa = direccion_empresa
                laboral.trabajo_actual = trabajo_actual

                laboral.save(commit=False)
                self.laboral_form(instance=laboral)

        persona = request.user.profile.persona
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'formulario':self.laboral_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class CompetenciaView(View):
    '''
    Clase para la renderización de los datos de conocimientos generales
    '''
    template='perfil/editar_formulario.html' # Plantilla que utilizará por defecto para renderizar
    mensaje = '' # Mensaje que se le mostrará al usuario
    tipo_mensaje = '' # Si el mensaje es de éxito o de error
    titulo = 'competencias' # Título a ser renderizado en la plantilla
    lista_filtros = '' # Listado filtrado de objetos que llegarán a la plantilla
    competencia_form = CompetenciaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})
    lista = ListaCompetencia.objects.exclude(tipo='academico')
    lista = lista.exclude(tipo='requerido')
    diccionario.update({'lista_competencia':lista})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        # Obtener la persona para renderizarla en la plantilla
        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        # Actualización del diccionario con el formulario
        self.diccionario.update({'formulario':self.competencia_form()})

        # Si se elimina una Competencia 
        if kwargs['palabra'] == 'eliminar':
            competencia = Competencia.objects.filter(usuario=persona.userprofile)
            if competencia.exists():
                for comp in competencia:
                    comp.delete()
                self.mensaje = u'Competencia ha sido eliminada exitosamente'
                self.tipo_mensaje = u'success'
            else:
                self.mensaje = u'Usted no tiene ninguna competencia que eliminar.'
                self.tipo_mensaje = u'warning'

            self.template = 'perfil/perfil.html'

        if kwargs.has_key('competencia_id') and not kwargs['competencia_id'] == None:
            if kwargs['palabra'] == 'editar':
                nueva = False

            try:
                competencia = Competencia.objects.get(id=int(kwargs['competencia_id']))
            except:
                raise Http404

            # Si el usuario de laboral no es el mismo al loggeado, retornar permisos denegados
            if competencia.usuario == usuario.profile:
                self.competencia_form = self.competencia_form(instance=conocimiento)
            else:
                raise PermissionDenied

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'formulario':self.competencia_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.competencia_form = self.competencia_form(request.POST)
        respuestas = request.POST.getlist('nivel')

        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            if kwargs['palabra'] == 'editar':
                for respuesta in respuestas:
                    nivel = respuesta.split('_')[0] # Optebnemos el nivel elegido
                    l_competencia = respuesta.split('_')[1] # Optenemos el ID de la competencia
                    l_competencia = ListaCompetencia.objects.get(id=l_competencia)

                    competencia = Competencia.objects.get(usuario=request.user.profile, competencia = l_competencia)
                    competencia.nivel = nivel
                    competencia.save()

                self.mensaje = u'Las competencias han sido editadas exitosamente'
                self.tipo_mensaje = u'success'

            else:
                # Si se crea información laboral 
                for respuesta in respuestas:
                    nivel = respuesta.split('_')[0] # Optebnemos el nivel elegido
                    l_competencia = respuesta.split('_')[1] # Optenemos el ID de la competencia
                    l_competencia = ListaCompetencia.objects.get(id=l_competencia)

                    competencia = Competencia.objects.create(usuario=request.user.profile, nivel=nivel, competencia=l_competencia)

                self.mensaje = u'Las competencias han sido creadas exitosamente'
                self.tipo_mensaje = u'success'


            self.template = 'perfil/perfil.html'

        persona = request.user.profile.persona

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})

        self.diccionario.update({'formulario':self.competencia_form})
        self.diccionario.update({'titulo':self.titulo})

        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class HabilidadView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    habilidad_form = HabilidadForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'habilidad'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.habilidad_form()})
        if kwargs.has_key('habilidad_id') and not kwargs['habilidad_id'] == None:
            nueva = False
            try:
                habilidad = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
            except:
                raise Http404

            if habilidad.usuario == persona.userprofile:
                self.habilidad_form = self.habilidad_form(instance=habilidad)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            habilidad = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
            habilidad.delete()

            self.mensaje = u'Habilidad eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.habilidad_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            habilidad = request.POST['habilidad']

            if kwargs['palabra'] == 'editar':
                # Si se edita una Educación
                # Búsqueda de variables con los IDs enviados por POST
                habilidad_obj = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
                habilidad_obj.habilidad = campo_habilidad

                habilidad_obj.save()

                self.mensaje = u'Habilidad editada exitosamente'
                self.tipo_mensaje = u'success'
            else:
                # Si se crea una Educación
                habilidad_obj = Habilidad.objects.create(usuario=persona.userprofile, habilidad=habilidad)
                self.mensaje = u'Habilidad creada exitosamente'
                self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.habilidad_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class ConocimientoView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    conocimiento_form = ConocimientoForm 
    titulo = 'conocimiento'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.conocimiento_form()})
        if kwargs.has_key('conocimiento_id') and not kwargs['conocimiento_id'] == None:
            try:
                conocimiento = Conocimiento.objects.get(id=int(kwargs['conocimiento_id']))
            except:
                raise Http404

            if conocimiento.usuario == persona.userprofile:
                self.conocimiento_form = self.conocimiento_form(instance=conocimiento)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'nueva':
            nueva = True
            if Conocimiento.objects.filter(usuario=persona.userprofile).exists():
                self.mensaje = u'Usted ya tiene conocimiento en base de datos, por favor edítela si es necesario'
                self.tipo_mensaje = u'error'
                self.template = 'perfil/perfil.html'

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            conocimiento = Conocimiento.objects.get(id=int(kwargs['conocimiento_id']))
            conocimiento.delete()

            self.mensaje = u'Conocimiento eliminado exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.conocimiento_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            conocimiento = request.POST['otros_conocimientos']

            if kwargs['palabra'] == 'editar':
                conocimiento = Conocimiento.objects.get(id=kwargs['conocimiento_id'])
                conocimiento.otros_conocimientos = request.POST['otros_conocimientos']
                conocimiento.save()

                self.mensaje = u'Conocimientos editados exitosamente'
                self.tipo_mensaje = u'success'
            else:
                if Conocimiento.objects.filter(usuario=persona.userprofile).exists():
                    self.mensaje = u'Usted ya tiene conocimientos guardados, por favor edítela si es necesario'
                    self.tipo_mensaje = u'error'
                else:
                    conocimiento = Conocimiento.objects.create(usuario=persona.userprofile, otros_conocimientos=conocimiento)
                    self.mensaje = u'Otros conocimientos creados exitosamente'
                    self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.conocimiento_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class IdiomaView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    idioma_form = IdiomaForm 
    titulo = 'idioma'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.idioma_form()})
        if kwargs.has_key('idioma_id') and not kwargs['idioma_id'] == None:
            try:
                idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))
            except:
                raise Http404

            if idioma.persona == persona:
                self.idioma_form = self.idioma_form(instance=idioma)
            else:
                raise PermissionDenied

        if kwargs['palabra'] == 'nueva':
            nueva = True
        else:
            idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            idioma.delete()

            self.mensaje = u'Idioma eliminado exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.idioma_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.userprofile_set.get_query_set()[0].persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            l_idioma = ListaIdiomas.objects.get(id=request.POST['idioma'])
            nivel_escrito = request.POST['nivel_escrito']
            nivel_leido = request.POST['nivel_leido']
            nivel_hablado = request.POST['nivel_hablado']

            # Buscamos que no se dupliquen idiomas
            idioma = Idioma.objects.filter(persona=persona, idioma=request.POST['idioma'])
            if idioma.exists() and idioma.count() > 1:
                self.mensaje = u'Usted ya tiene %s cargado en base de datos, por favor edítela si es necesario' %(request.POST['idioma'])
                self.tipo_mensaje = u'error'
                self.template = 'perfil/editar_formulario.html'
                self.idioma_form=idioma_form(request)
            else:
                if kwargs['palabra'] == 'editar':
                    idioma = Idioma.objects.get(id=kwargs['idioma_id'])
                    idioma.idioma = l_idioma
                    idioma.nivel_escrito = nivel_escrito
                    idioma.nivel_leido = nivel_leido
                    idioma.nivel_hablado = nivel_hablado
                    idioma.save()

                    self.mensaje = u'Idioma editado exitosamente'
                    self.tipo_mensaje = u'success'
                else:
                    idioma = Idioma.objects.create(persona=persona, idioma=l_idioma, nivel_escrito=nivel_escrito, nivel_leido=nivel_leido, nivel_hablado=nivel_hablado)
                    self.mensaje = u'Idioma creado exitosamente'
                    self.tipo_mensaje = u'success'

                self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.idioma_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

