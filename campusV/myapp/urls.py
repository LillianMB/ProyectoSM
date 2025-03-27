from django.urls import path
from .views import registro, iniciar_sesion, cerrar_sesion, home
from . import views

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('', home, name='home'),
    path("agrega_grupo/", views.agrega_grupo, name="agrega_grupo"),
    path("agregar_equipo/", views.agregar_equipo, name="agregar_equipo"),
    path("agregar_actividad/", views.agregar_actividad, name="agregar_actividad"),
    path("obtener_grupos/", views.obtener_grupos, name="obtener_grupos"),
    path("obtener_grupo/<int:id>/", views.obtener_grupo, name="obtener_grupo"),
    path("obtener_equipos/<int:idGrupo>/", views.obtener_equipos, name="obtener_equipos"),
    path("obtener_equipo/<int:idEquipo>/", views.obtener_equipo, name="obtener_equipo"),
    path("obtener_actividades/", views.obtener_actividades, name="obtener_actividades"),
    path('obtener_actividad/', views.obtener_actividad, name='obtener_actividad'),
    path("obtener_calendario/", views.obtener_calendario, name="obtener_calendario"),
    path("alumno/", views.alumno, name="alumno"),
    path("obtener_alumnos/", views.obtener_alumnos, name="obtener_alumnos"),
    path("guardar_tarea/", views.guardar_tarea, name="guardar_tarea"),
    path("revolver_roles/", views.revolver_roles, name="revolver_roles"),
    path('obtenerNotificaciones', views.obtener_notificaciones, name='obtener_notificaciones'),
]
