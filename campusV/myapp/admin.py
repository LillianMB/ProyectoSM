from django.contrib import admin
from .models import Usuario, Grupos, Equipos, Actividades, Preguntas, Respuestas, Respuestas_Alumno, Calendario, Calificaciones, Notificacion


class CalificacionesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Calificaciones._meta.fields if field.name != 'archivoTarea']
class EquipoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Equipos._meta.fields]

class GrupoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Grupos._meta.fields]


class UsuarioAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Usuario._meta.fields if field.name != 'password']

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Grupos, GrupoAdmin)
admin.site.register(Equipos, EquipoAdmin)
admin.site.register(Actividades)
admin.site.register(Preguntas)
admin.site.register(Respuestas)
admin.site.register(Respuestas_Alumno)
admin.site.register(Calendario)
admin.site.register(Calificaciones, CalificacionesAdmin)
admin.site.register(Notificacion)