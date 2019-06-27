import subprocess
import os,sys,shutil,glob
from shlex import split as shplit
from filehandler import python_findline as pf, python_writeline as pw,htmlfind_and_replace as hr
import htmlparser as html
import djangofiles as df
from htmlparser import color

if len(sys.argv) !=3:
    print("Error : {} <ProjectName> <Html Files Folder Name>".format(sys.argv[0]))
    exit()


#constants
HTML_FILE_NAMES          = [f for f in glob.glob("{}/*.html".format(os.environ['PWD']+'/'+sys.argv[2]))]
PROJECT_NAME             = shplit(sys.argv[1])[0]
PROJECT_HOME             = subprocess.check_output('pwd').strip().decode('utf-8')
SETTINGS                 = '{}/{}/settings.py'.format(PROJECT_HOME,PROJECT_NAME)
URLS                 = '{}/{}/urls.py'.format(PROJECT_HOME,PROJECT_NAME)
DJANGO_PROJECT           = 'django-admin startproject {} .'.format(PROJECT_NAME)
INSTALL_DJANGO_IN_VIRENV = 'pipenv install django'
PIPENV_RUN               = 'pipenv run'
APPS                     = []
temp_file = '{}/{}'.format(PROJECT_HOME,'templates')
if sys.argv[1] == 'setup':
    if not os.path.exists(temp_file):
        os.mkdir(temp_file)
    for i in HTML_FILE_NAMES:
        shutil.copy(i,temp_file)
        if len(hr(i,"[Model  "))==0:
            print(color('rb'),"# Fill the appropriate HTML file details ",color('gb'),i,color())

def pip_env_run(args):
    return '{} {}'.format(PIPENV_RUN,args)

def run_cmd(args,pip=None):
    #CD = subprocess.check_output('pwd').strip().decode('utf-8') 
    print(color('rb'),'Running Command',color('gb'),args,color())
    if pip:
        subprocess.run(shplit(pip_env_run(args)))
    else:
        subprocess.run(shplit(args))

def createapp(app):
    run_cmd('python manage.py startapp {}'.format(app),'pipenv')
    line_no = pf(SETTINGS,'INSTALLED')['Insert']
    pw(SETTINGS,"    '{}',\n".format(app),line_no) 
    shutil.copyfile('{}/{}/urls.py'.format(PROJECT_HOME,PROJECT_NAME),'{}/{}/urls.py'.format(PROJECT_HOME,app))
    APPS.append("{}/{}".format(PROJECT_HOME,app))

def default_setup():
    htmlfiles = []
    error=False
    if sys.argv[1] == 'setup':
        for i in HTML_FILE_NAMES:
            if len(hr(i,"[Model  "))==0:
                hr(i,['<form'],insert='<!--[Model    : None]-->')
                hr(i,['<form'],insert='<!--[FormType : None]-->')
                hr(i,['<form'],insert='<!--[FormName : None]-->')
                hr(i,['<form'],insert='<!--[Redirect : None]-->')
                pw(i,'<!--[TemplateName  : None]-->\n',1)
                pw(i,'<!--[LoginRequired : None]-->\n',2)
                pw(i,'<!--[Path          : None]-->\n',3)
            htmlfiles.append(html.parse_html(i,setup=True))
            for j in ['Model','FormName','TemplateName','Path']:
                p = hr(i,"[%s" % (j))
                for ii in p:
                    if ii[1].split(':')[1].strip(']-->').strip() == 'None':
                        print(color('r'),"\nFile    : ",color('gb')," {}".format(i.split('/')[-1]),color())
                        print(color('r'),"Error   : ",color('wb'),"Fill the HTML file details",color())
                        print(color('r'),'Details : ',color('wb'),"LINE %s, %s is None " % (ii[0],j),color())
                        error=True
        if error:
            exit()
    else:
        CONF = []
        for c,i in enumerate(HTML_FILE_NAMES):
            CONF.append([])
            htmlfiles.append(html.parse_html(i))
            for j in ['Model','FormType','FormName','Redirect']:
                CONF[c].append(hr(i,"[%s" % (j)))
         #  print(i,'\n',CONF,'\n')
            shutil.copy(i,temp_file)
         
        run_cmd(INSTALL_DJANGO_IN_VIRENV)
        run_cmd(DJANGO_PROJECT,'pipenv')
        line_no = pf(SETTINGS,'\'DIRS\': [],')['line_no']
        pw(SETTINGS,"        'DIRS': [os.path.join(BASE_DIR, 'templates')],\n",line_no,replace=1) 
        createapp('NEWAPP')

# Parsing html files
# Take values from htmlfiles list and write to the django files
# Creating a form djangofiles object
        df.dw(APPS[0]+'/forms.py','')
        fm = df.form(**{'formfile' : APPS[0]+'/forms.py'})
        fm.write(imports="from django import forms\n")
        fm.write(imports="from django.contrib.auth.forms import UserCreationForm\n")
        fm.write(imports="from django.contrib.auth.models import User\n")

# Creating a model djangofiles object
        df.dw(APPS[0]+'/models.py','',tt='w')
        mod = df.model(**{'modelfile' : APPS[0]+'/models.py'})
        mod.write(imports="from django.db import models\n")
        mod.write(imports="from django.urls import reverse\n")

# Creating a view djangofiles object
        df.dw(APPS[0]+'/views.py','',tt='w')
        view = df.view(**{'viewfile' : APPS[0]+'/views.py'})
        view.write(imports="from django.shortcuts import render\n")

# Creating a url djangofiles oject
        url = df.url(**{'urlfile' : APPS[0]+'/urls.py'})
        rooturl = df.url(**{'urlfile' : URLS})
        models = []
        forms = []
        for count,i in enumerate(htmlfiles):

            path = hr(i.filename,['[Path       '])[0][1].split(':')[1].strip(']-->').strip()
            template_name = hr(i.filename,['[TemplateName '])[0][1].split(':')[1].strip(']-->').strip()
            for co,form in enumerate(i.forms):
                printval = []
                names = []
                model_name = CONF[count][0][co][1].split(':')[1].strip(']-->').strip()
                form_name  = CONF[count][2][co][1].split(':')[1].strip(']-->').strip()
                forms.append(form_name)
                if model_name not in models:
                    models.append(model_name)
                    mod.write("\nclass %s(models.Model):" % (model_name)) 

                for inputs in form[1].input_tags:
                    a_in = []
                    name = inputs.__dict__['_name']
                    in_type = inputs.__dict__['_type']
                    
# Writing to the forms.py file in the django APP
                    if name ==  'csrfmiddlewaretoken' or in_type == 'submit' or in_type == 'select':
                        continue
                    names.append(name)
# Writing to the models.py  file in the django APP
                    mod.check(name,in_type)

# Replace the values in the HTML file and save to the Template files
                    newline = '{{ form.%s }}' % (name)
                    if in_type == "textarea":
                        ttt = inputs.__dict__
                        ttt.pop('_type')
                        par = list(ttt.values())
                        par.append('textarea')
                    else:
                        par = list(inputs.__dict__.values())
                        par.append('input')
                    hr("{}/{}".format(temp_file,i.filename.split('/')[-1]),par,newline)
                    view.write("")

                    for key in list(inputs.__dict__.keys()):
                        if key != '_name':
                            a_in.append("'{}' : '{}'".format(key[1:],inputs.__dict__[key]))
                    val = ','.join(a_in).strip('')
                    textval = "TextInput"
                    if in_type == "textarea":
                        textval = "Textarea"
                    #elif in_type == "select":
                    printval.append("%s = forms.CharField(widget=forms.%s(attrs={%s}))" % (name,textval,val))   
                fm.write("\nclass %s(forms.ModelForm):" % (form_name))
                for qq in printval:
                    fm.write("    {}".format(qq))
                fm.write("    class Meta:")
                fm.write("        model = %s" %  (model_name))
                fm.write("        fields = %s" % (str(names)))
                view.write("\ndef %s_view(request):\n\
    form = %s()\n\
    if request.method == 'POST':\n\
        form = %s(request.POST)\n\
        if form.is_valid():\n\
            topic = form.save(commit=False)\n\
            topic.save()\n\
            form = %s()\n\
            return redirect('home')\n\
    return render(request,'%s', {'form' : form,})\n" % (form_name,form_name,form_name,form_name,i.filename.split('/')[-1]))
            url.write("    path('%s', %s_view, name='%s'),\n" % (path,form_name,template_name) ) 
        rooturl.write("    path('', include('%s.urls')),\n" % (APPS[0].split('/')[-1]))
        rooturl.write(imports = "from django.urls import include\n")
        view.write(imports="from django.shortcuts import redirect\nfrom .forms import %s" % (','.join(forms)))
        url.write(imports="from .views import %s_view\n" % ('_view, '.join(forms)))
        fm.write(imports="from .models import %s\n" % (','.join(models)))
        df.dw(APPS[0]+'/admin.py',"from .models import %s\n\n" % (','.join(models)))
        for i in models:
            df.dw(APPS[0]+'/admin.py',"admin.site.register(%s)\n" % (i))

def finish():
    run_cmd('python manage.py makemigrations','pipenv')
    run_cmd('python manage.py migrate','pipenv')
    run_cmd('python manage.py createsuperuser','pipenv')
    print("Run ",color('gb'), "`python manage.py runserver`",color(), " to start local server")

def main():
    default_setup()
    if sys.argv[1] != 'setup':
        finish()
    else:
        print("\n",color('rb'),"# Setup Complete",color())

if __name__=='__main__':
    main()
