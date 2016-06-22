from django.contrib import admin
from .models import XMLFile,XMLData

# Register your models here.
# Register your models here.

class XMLDataAdmin(admin.ModelAdmin):

    show_full_result_count = True
    list_display = ('nodeID','nodeName','nodeparentName','nodeattribute', 'nodedata','nodeparentID','linktoparent')
    list_filter = ('nodeName','nodeparentName',)
    search_fields = ['id','nodeName','nodedata',]

admin.site.register(XMLData,XMLDataAdmin)
