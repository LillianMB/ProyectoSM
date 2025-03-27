from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import RegistroUsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Grupos, Equipos, Actividades, Preguntas, Respuestas, Usuario, Calendario, Calificaciones, Respuestas_Alumno, Notificacion
from django.utils.dateparse import parse_date
from django.db.models import Avg
from datetime import datetime
import random

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("alumno" if user.tipo == "alumno" else "home")
    else:
        form = RegistroUsuarioForm()
    return render(request, "registro.html", {"form": form})

def iniciar_sesion(request):
    if request.method == "POST":
        correo = request.POST['email']
        contraseña = request.POST['password']
        user = authenticate(request, username=correo, password=contraseña)
        if user:
            login(request, user)
            return redirect("alumno" if user.tipo == "alumno" else "home")
    return render(request, "login.html")

def cerrar_sesion(request):
    logout(request)
    return redirect('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'home.html')

def alumno(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    usuario = Usuario.objects.get(id=request.user.id)
    
    # Obtener el equipo del usuario logueado
    equipo = Equipos.objects.filter(id=usuario.idEquipo).first()
    
    # Obtener todos los usuarios del equipo, excluyendo al usuario logueado
    usuarios_equipo = Usuario.objects.filter(idEquipo=usuario.idEquipo).exclude(id=usuario.id).exclude(idEquipo = None)
    
    # Obtener los registros del calendario
    calendario = Calendario.objects.all()
    suma = 0
    
    fecha_actual = datetime.now()
    for cal in calendario:
        puede_subir = True
        calificacion = Calificaciones.objects.filter( idActividad = cal.idActividad.id, idUsuario = usuario.id ).first()

        if calificacion:
            puede_subir = False
            suma = suma + calificacion.Calificacion
        
        if datetime.now() > datetime.combine(cal.Fecha_limite, datetime.min.time()):
            puede_subir = False

        cal.calificacion = calificacion
        cal.puede_subir = puede_subir

    Completado = suma / len(calendario)



    return render(request, "alumno.html", {
        "usuario": usuario,
        "equipo": equipo,
        "calendario": calendario,
        "Completado": Completado,
        "Restante": 100 - Completado,
        "usuarios_equipo": usuarios_equipo  # Pasar los usuarios del equipo
    })


@csrf_exempt
def agrega_grupo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        grupo = Grupos.objects.create(Nombre=data["Nombre"])
        if "usuarios" in data:
            usuarios = Usuario.objects.filter(id__in=data["usuarios"])
            for usuario in usuarios:
                usuario.idGrupo = grupo.id
                usuario.save()
        return JsonResponse({"id": grupo.id, "Nombre": grupo.Nombre})

@csrf_exempt
def agregar_equipo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        equipo = Equipos.objects.create(Nombre=data["Nombre"], idGrupo=data["idGrupo"])
        if "usuarios" in data:
            usuarios = Usuario.objects.filter(id__in=data["usuarios"])
            for usuario in usuarios:
                usuario.idEquipo = equipo.id
                usuario.idGrupo = data["idGrupo"]
                usuario.save()
        
        Notificacion.objects.create(texto= "Se ha creado un nuevo grupo")

        return JsonResponse({"id": equipo.id, "Nombre": equipo.Nombre})

@csrf_exempt
def agregar_actividad(request):
    if request.method == "POST":
        data = json.loads(request.body)
        actividad = Actividades.objects.create(Nombre=data["Nombre"], Descripcion=data["Descripcion"], tipo=data["tipo"])

        fecha_actividad = datetime.strptime(data["Fecha_limite"], "%Y-%m-%d").date()
        Calendario.objects.create(idActividad=actividad, Fecha_limite=fecha_actividad)


        if data["tipo"] == "Quizz":
            for pregunta_data in data["preguntas"]:
                pregunta = Preguntas.objects.create(idActividad=actividad.id, Texto=pregunta_data["pregunta"])
                for respuesta_data in pregunta_data["respuestas"]:
                    Respuestas.objects.create(idPregunta=pregunta.id, Texto=respuesta_data["Texto"], eslaCorrecta=respuesta_data["eslaCorrecta"])
        
        Notificacion.objects.create(texto= "Se ha agregado una nueva actividad")

        return JsonResponse({"id": actividad.id, "Nombre": actividad.Nombre})

def obtener_grupos(request):
    grupos = list(Grupos.objects.values())
    return JsonResponse(grupos, safe=False)

def obtener_grupo(request, id):
    grupo = get_object_or_404(Grupos, id=id)
    alumnos = Usuario.objects.filter(idGrupo=id).values()

    for alumno in alumnos:
        promedio = Calificaciones.objects.filter(idUsuario = alumno["id"]).aggregate(promedio=Avg('Calificacion'))['promedio']
        alumno["promedio"] = promedio

    return JsonResponse({"id": grupo.id, "Nombre": grupo.Nombre, "Alumnos": list(alumnos)})

def obtener_equipos(request, idGrupo):
    equipos = Equipos.objects.filter(idGrupo=idGrupo).values()
    equipos_lista = []
    for equipo in equipos:
        alumnos = Usuario.objects.filter(idEquipo=equipo["id"]).values()
        for alumno in alumnos:
            alumno["Calificaciones"] = list(Calificaciones.objects.filter(idUsuario=alumno["id"]).values())
        equipos_lista.append({"Equipo": equipo, "Alumnos": list(alumnos)})
    return JsonResponse(equipos_lista, safe=False)

def obtener_equipo(request, idEquipo):
    equipo = get_object_or_404(Equipos, id=idEquipo)
    alumnos = Usuario.objects.filter(idEquipo=idEquipo).values()
    for alumno in alumnos:
        alumno["Calificaciones"] = list(Calificaciones.objects.filter(idUsuario=alumno["id"]).values())
    return JsonResponse({"id": equipo.id, "Nombre": equipo.Nombre, "Alumnos": list(alumnos)})

def obtener_actividades(request):
    actividades = list(Actividades.objects.values())
    return JsonResponse(actividades, safe=False)

def obtener_actividad(request):
    actividad_id = request.GET.get('id')
    actividad = Actividades.objects.get(id=actividad_id)
    
    # Obtener preguntas y respuestas
    preguntas = []
    for pregunta in Preguntas.objects.filter(idActividad=actividad_id):
        respuestas = []
        for respuesta in Respuestas.objects.filter(idPregunta=pregunta.id):
            respuestas.append({
                "id": respuesta.id,
                'texto': respuesta.Texto,
                'eslaCorrecta': respuesta.eslaCorrecta
            })
        preguntas.append({
            "id": pregunta.id,
            'texto': pregunta.Texto,
            'respuestas': respuestas
        })
    
    # Enviar los datos como JSON
    return JsonResponse({
        'tipo': actividad.tipo,
        'nombre': actividad.Nombre,
        'descripcion': actividad.Descripcion,
        'preguntas': preguntas
    })

@csrf_exempt
def obtener_calendario(request):
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if start_date and end_date:
        start_date = datetime.fromisoformat(start_date[:-6]).date()  # Remueve la zona horaria
        end_date = datetime.fromisoformat(end_date[:-6]).date()  # Remueve la zona horaria
        eventos = Calendario.objects.filter(Fecha_limite__range=[start_date, end_date])
    else:
        eventos = Calendario.objects.all()

    eventos_json = [
        {
            "id": evento.idActividad.id,
            "title": evento.idActividad.Nombre,
            "start": evento.Fecha_limite.isoformat(),
            "end": evento.Fecha_limite.isoformat(),
            "extendedProps": {
                "descripcion": evento.idActividad.Descripcion
            }
        }
        for evento in eventos
    ]

    return JsonResponse(eventos_json, safe=False)

def obtener_alumnos(request):
    alumnos = list(Usuario.objects.filter(tipo="alumno").values())
    return JsonResponse(alumnos, safe=False)
    
@csrf_exempt
def guardar_tarea(request):
    if request.method == "POST":
        try:
            data = request.POST
            id_actividad = data.get("idActividad")
            actividad = Actividades.objects.get(id=id_actividad)
            usuario = request.user  # Suponiendo que el usuario está autenticado

            if actividad.tipo == "Quizz":
                respuestas_json = json.loads(data.get("respuestas", "[]"))
                correctas = 0
                total = len(respuestas_json)
                for respuesta in respuestas_json:
                    respuesta_obj = Respuestas.objects.get(id=respuesta["idRespuesta"])
                    if respuesta_obj.eslaCorrecta:  # Comprobar si la respuesta es correcta
                        correctas += 1

                    Respuestas_Alumno.objects.create(
                        idPregunta=respuesta["idPregunta"],
                        idRespuesta=respuesta["idRespuesta"]
                    )

                if total > 0:
                    promedio = correctas / total
                else:
                    promedio = 0

                calificacion, _ = Calificaciones.objects.get_or_create(
                    idUsuario=usuario.id, idActividad=actividad.id,
                    Calificacion = 100 * promedio
                )
                calificacion.save()
            else:
                archivo = request.FILES.get("archivo")
                archivo_bytes = archivo.read()
                if archivo:
                    calificacion, _ = Calificaciones.objects.get_or_create(
                        idUsuario=usuario.id, idActividad=actividad.id,
                        Calificacion = 100
                    )
                    calificacion.archivoTarea = archivo_bytes
                    calificacion.save()

            return JsonResponse({"mensaje": "Tarea guardada correctamente"}, status=200)

        except Actividades.DoesNotExist:
            return JsonResponse({"error": "Actividad no encontrada"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def revolver_roles(request):
    
    Notificacion.objects.create(texto= "Se te ha asignado un nuevo Rol")

    if request.method == 'POST':
        # Obtener el id del grupo
        id_grupo = request.POST.get('idGrupo')

        if not id_grupo:
            return JsonResponse({'error': 'ID de grupo no proporcionado'}, status=400)

        # Obtener todos los usuarios del grupo
        usuarios = Usuario.objects.filter(idGrupo=id_grupo)

        # Agrupar usuarios por idEquipo
        equipos = {}
        for usuario in usuarios:
            if usuario.idEquipo not in equipos:
                equipos[usuario.idEquipo] = []
            equipos[usuario.idEquipo].append(usuario)

        # Roles disponibles
        roles = ['Scrum Master', 'Product Owner', 'Developer 1', 'Developer 2']

        # Asignar roles aleatorios a los usuarios de cada equipo
        for id_equipo, miembros in equipos.items():
            # Si hay menos de 4 miembros, el rol de "Developer" será asignado aleatoriamente
            random.shuffle(roles)  # Barajar los roles

            for i, miembro in enumerate(miembros):
                if i < len(roles):
                    miembro.rol = roles[i]
                    miembro.save()  # Guardar el rol asignado al usuario

        return JsonResponse({'message': 'Roles revueltos con éxito.'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_notificaciones(request):
    # Obtener todas las notificaciones
    notificaciones = Notificacion.objects.all().values('id', 'texto', 'fechaEnvio')

    # Convertir las notificaciones a un formato adecuado para JSON
    notificaciones_list = list(notificaciones)

    # Retornar las notificaciones como respuesta JSON
    return JsonResponse(notificaciones_list, safe=False)