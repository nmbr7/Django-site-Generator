from filehandler import python_findline as pf, python_writeline as pw, django_write as dw



class model(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
        self.importline = 0
    def write(self,lines=None,imports=None):
        if imports:
            pw(self.modelfile,imports,self.importline)
            self.importline +=1
        if lines:
            dw(self.modelfile,lines)
    def check(self,name,input_type):
        params = ""
        if input_type == 'email':
            fieldtype = "EmailField"
        elif input_type == 'date':
            fieldtype = "DateField"
        elif input_type == 'textarea':
            fieldtype = "TextField"
        elif input_type == 'number':
            fieldtype = "DecimalField"
            params = "max_digits=5, decimal_places=2"
        else:
            fieldtype = "CharField"
            params = "max_length=100"
        self.write("    %s = models.%s(%s)" % (name,fieldtype,params))


class view(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
        self.importline = 0
    def write(self,lines=None,imports=None):
        if imports:
            pw(self.viewfile,imports,self.importline)
            self.importline +=1
        if lines:
            dw(self.viewfile,lines)



class url(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
        self.importline = 0

    def write(self,lines=None,imports=None):
        if imports:
            pw(self.urlfile,imports,self.importline)
            self.importline +=1
        if lines:
            lineno = pf(self.urlfile,'urlpatterns')
            pw(self.urlfile,lines,lineno['Insert'])

class form(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
        self.importline = 0

    def write(self,lines=None,imports=None):
        if imports:
            pw(self.formfile,imports,self.importline)
            self.importline +=1
        if lines:
            dw(self.formfile,lines)

    #def djangoforms()

