import lxml.html as html,cssselect
import re
from filehandler import htmlfind_and_replace as hr1

def color(color='n'):
    if color =="r":
        return "\033[1;31m"
    elif color =="g":
        return "\033[1;32m"
    elif color =="w":
        return "\033[m\033[1;37m"
    elif color =="rb":
        return "\033[1;31;40m"
    elif color =="gb":
        return "\033[1;32;40m"
    elif color =="wb":
        return "\033[m\033[1;37;40m"
    else:
        return "\033[m"

class form(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
        self.input_tags = []

    def view(self):
        print(self.__dict__,'\n*********************\n')
        for i in self.input_tags:
            print(i.__dict__,'\n')

    def add_tag(self,**kwargs):
        self.input_tags.append(input_tag(**kwargs))

class input_tag(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})

class htmlfile(object):
    def __init__(self,**kwargs):
        self.__dict__.update({k: v for k,v in locals()['kwargs'].items()})
error = False
def check(i,val,fileloc):
    global error
    reg = re.compile("(?=\W)(?=\S)(?=[^\-])")
    for j in i.cssselect(val):
        if ('name' not in j.keys()) or (j.attrib['name'] is None) or (j.attrib['name'].strip()==''):
            print(color('r'),"\nFile   : ",color('gb')," {}".format(fileloc.split('/')[-1]),color())
            print(color('r'),"Error  : ",color('wb'),"`name` attribute not specified or is empty in %s tag" % (val),color())
            print(color('r'),"Attrib : ",color('wb'),j.items(),color())
            error=True
        for p in list(j.values()):
            if reg.search(p):
                print(color('r'),"\nFile   : ",color('gb')," {}".format(fileloc.split('/')[-1]),color())
                print(color('r'),"Error  : ",color('wb')," Invalid values specified in %s tag" % (val),color())
                print(color('r'),"Attrib : ",color('wb'),p,color())
                error=True
    return error
 
def parse_html(fileloc,setup=None):
    che = False
    global error
    root = html.parse(fileloc).getroot()
    forms = []
    if setup:
        for index,i in enumerate(root.cssselect("form")):
            if index==0:
                print("\n",color('rb'),"# Checking validity of form",color())
            error = check(i,'input',fileloc)
            error = check(i,'textarea',fileloc)
            #error = check(i,'select',fileloc)

        if error:
            exit()
    else:
        for index,i in enumerate(root.cssselect("form")):
            newline = "<form" 
            for k,v in i.items():
                if k =='method':
                    che = True
                    v = 'POST'
                newline += " %s='%s'" % (k,v)
            if not che:
                k = 'method'
                v = 'POST'
                newline += " %s='%s'" % (k,v)
            newline +=">{% csrf_token %}"
            par = i.attrib.values()
            par.append('form')
            hr1(fileloc,par,newline)

            che = False
            for qw in i.cssselect('button'):
                newline = "<button" 
                for k,v in qw.items():
                    if k =='type':
                        che = True
                        v = 'submit'
                    newline += " %s='%s'" % (k,v)
                if not che:
                    k = 'type'
                    v = 'submit'
                    newline += " %s='%s'" % (k,v) 
                newline +=">"
                par = qw.attrib.values()
                par.append('button')
                hr1(fileloc,par,newline)

            fkwarg = {"_{}".format(k):v for k,v in i.items()}
            forms.append((i,form(**fkwarg)))
            for j in i.cssselect("input"):
                kwargs = {"_{}".format(k):v for k,v in j.items() }
                forms[index][1].add_tag(**kwargs)
            for j in i.cssselect("textarea"):
                kwargs = {"_{}".format(k):v for k,v in j.items() }
                kwargs.update({'_type':'textarea'})
                forms[index][1].add_tag(**kwargs)
                '''for j in i.cssselect('select'):
                vals = []
                kwargs = {"_{}".format(k):v for k,v in j.items()}
                for op in j.cssselect('option'):
                    vals.append(op.text)
                kwargs.update({'_type':'select','_options':vals})
                forms[index][1].add_tag(**kwargs)'''
    return htmlfile(**{'filename':fileloc,'forms':forms})

    for  i in forms:
        i[1].view()

