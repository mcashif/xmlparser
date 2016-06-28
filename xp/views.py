from django.shortcuts import render
from .models import XMLFile,XMLData
from .serializers import XMLSerializer
from django.conf import settings
from rest_framework import routers, serializers, viewsets
from rest_framework.parsers import MultiPartParser,FileUploadParser,FormParser
from rest_framework.response import Response
from lxml import etree
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from .forms import DocumentForm
from django.template import RequestContext
import os
import stat
import time
import shutil

# Create your views here.



#main function to populate DB
def populateDB(path):

    parent="Root"
    idParent=0
    idNode=0


    XMLData.objects.all().delete()
    parser = etree.XMLParser(load_dtd= True)
    tree = etree.parse(settings.PROJECT_ROOT+"/media/"+path,parser)
    for el in tree.iter():
             if etree.iselement(el):

                if etree.iselement(el.getparent()):
                    parent= el.getparent().tag
                    linkparent=tree.getpath(el.getparent())
                    obj=XMLData.objects.filter(linktoparent=linkparent)
                    idParent=obj[0].nodeID



                link=tree.getpath(el)
                txtData=getTxtData(el)
                newRecord = XMLData(nodeID=idNode, nodeName = el.tag, nodeparentName = parent, nodeparentID = idParent ,nodeattribute = str(dict(el.attrib)), nodedata =  txtData, linktoparent= link)
                newRecord.save()
                idNode=idNode+1

# some utility functions:
def getParentID(node):

    for i in range(0, len(dbNodes)):
        if(dbNodes[i][0]==node.getparent()):
            return dbNodes[i][1]

    return 0

def getTxtData(el):

    txtData=""

    if(el.text):
        txtData=el.text
    else:
        if(el.tail):
            txtData=el.tail

    return txtData

def isendNode(node):

    if(node.getchildren()):
      return False
    else:
      return True

def getRealNext(node):

    for el in node.findall('.//'):
        if el==node:
            continue
        if etree.iselement(el):
           return el

    return False


#clean XML file from self closing tags and put non-tail data under tags.
def cleanXMLLevel2(path):

    parser = etree.XMLParser(load_dtd= True)
    tree = etree.parse(settings.PROJECT_ROOT+"/media/"+path,parser)


    for el in tree.iter():
             if etree.iselement(el):
                    nextReal= getRealNext(el)
                    if etree.iselement(nextReal) and isendNode(nextReal):
                        strVal=str(etree.tostring(nextReal))
                        if "/>" in strVal:
                            tag=nextReal.tag
                            strText=el.text
                            el.text=""
                            sub_node_element = etree.XML("<" + tag + "/>")
                            el.insert(0,sub_node_element)
                            sub_node_element.tail=strText


    tree.write(settings.PROJECT_ROOT+"/media/"+path, pretty_print=True)


#it has been found XML file has some useless : element and those are needed to be deleted
def cleanXMLLevel1(path):

    parser = etree.XMLParser(load_dtd= True)
    tree = etree.parse(settings.PROJECT_ROOT+"/media/"+path,parser)


    for el in tree.iter():
             if etree.iselement(el):
                if el.text==":" :
                    if isendNode(el):
                        el.getparent().text=el.getparent().text+":"
                        el.getparent().remove(el)


    tree.write(settings.PROJECT_ROOT+"/media/"+path, pretty_print=True)

def dumpDB():
    db_User_Name = 'xmlparse'
    DB_User_Password = 'test1234'
    DB_Name = 'xmlparse$xmlparser'
    backupDir = '/home/xmlparse/xmlparser/media'

    mysqldump_cmd = "mysqldump -u " + db_User_Name + " --password='" + DB_User_Password + "' -h xmlparse.mysql.pythonanywhere-services.com  " +  "'xmlparse$xmlparser' " + "xp_xmldata >" + backupDir + "/" + "dump.sql"
    os.system(mysqldump_cmd)

#Helper Function Remove Directory
def _remove_readonly(fn, path_, excinfo):
    # Handle read-only files and directories
    if fn is os.rmdir:
        os.chmod(path_, stat.S_IWRITE)
        os.rmdir(path_)
    elif fn is os.remove:
        os.lchmod(path_, stat.S_IWRITE)
        os.remove(path_)


def force_remove_file_or_symlink(path_):
    try:
        os.remove(path_)
    except OSError:
        os.lchmod(path_, stat.S_IWRITE)
        os.remove(path_)


# Code from shutil.rmtree()
def is_regular_dir(path_):
    try:
        mode = os.lstat(path_).st_mode
    except os.error:
        mode = 0
    return stat.S_ISDIR(mode)


def clear_dir(path_):
    for filename in os.listdir(path_):
        if filename.endswith(".xml"):
            filepath = os.path.join(path_, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)

# ViewSets API call to load XML.
# http -f -a mcashif:abc12345 --timeout=25000 PUT http://127.0.0.1:8000/test/ file_name=kashif docfile@/Users/Apple/Downloads/yy.xml
class XMLViewSet(viewsets.ModelViewSet):

        queryset = XMLFile.objects.all()
        serializer_class = XMLSerializer
        parser_classes = (MultiPartParser,FormParser,)
        def put(self, request, format=None):

            #CLear All Old Data in Database
            clear_dir(settings.PROJECT_ROOT+"/media/dbdata/")
            XMLFile.objects.all().delete()
            #////////////////////////////////////////////////////
            #Read Excel and load into Database for processing.....
            data=request.FILES['file_data']
            newdoc = XMLFile(file_data = data)
            newdoc.save()

            cleanXMLLevel1(newdoc.file_data.name)
            cleanXMLLevel2(newdoc.file_data.name)
            populateDB(newdoc.file_data.name)
            dumpDB()

            timestr = time.strftime("%Y%m%d-%H%M%S")
            timestr=timestr+".sql"
            #dump_file = open('/home/xmlparse/xmlparser/media/dump.sql', 'r')
            path=settings.PROJECT_ROOT+"/media/dump.sql"
            dump_file = open(path, 'r')

            response = HttpResponse(dump_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="%s"' % timestr
            return response



def index(request):
        # Handle file upload
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():

                #CLear All Old Data in Database
                clear_dir(settings.PROJECT_ROOT+"/media/dbdata/")
                XMLFile.objects.all().delete()
                #////////////////////////////////////////////////////
                #Read Excel and load into Database for processing.....

                newdoc = XMLFile(file_data = request.FILES['docfile'])
                newdoc.save()

                cleanXMLLevel1(newdoc.file_data.name)
                cleanXMLLevel2(newdoc.file_data.name)
                populateDB(newdoc.file_data.name)
                dumpDB()

                timestr = time.strftime("%Y%m%d-%H%M%S")
                timestr=timestr+".sql"
                #dump_file = open('/home/xmlparse/xmlparser/media/dump.sql', 'r')
                path=settings.PROJECT_ROOT+"/media/dump.sql"
                dump_file = open(path, 'r')

                response = HttpResponse(dump_file, content_type='application/force-download')
                response['Content-Disposition'] = 'attachment; filename="%s"' % timestr
                return response
        else:
            form = DocumentForm() # A empty, unbound form


        # Render GUI
        return render_to_response(
            'xp/index.html',
            {'form': form},
            context_instance=RequestContext(request)
        )

        return HttpResponse(template.render(context, request))
