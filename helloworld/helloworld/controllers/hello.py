import logging
import rascal

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from helloworld.lib.base import BaseController, render

log = logging.getLogger(__name__)

class HelloController(BaseController):

    def editor(self):
        c.fileurl = request.params['fileurl']
        c.sourcefile = request.params['sourcefile']
        return render('/editor.mako')

    def filetree(self):
        return render('/filetree.mako')

    def form(self):
        return render('/form.mako')

    def get_dirlist(self):
        import filetree
        return filetree.dirlist(request)

    def index(self):
        c.sourcefile = "index.mako"
        c.fileurl = "/hello/index"
        c.pin = rascal.read_pin(66)
        return render('/index.mako')

    def save(self):
        path = '/home/root/helloworld/helloworld/public/'
        c.fileurl = request.params['fileurl']
        c.sourcefile = request.params['sourcefile']
        f = open(path + str(c.sourcefile), 'w')
        f.write(request.params['text'])
        f.close()
        return render('/filetree.mako')

    def toggle(self):
        if(request.params['target_state'] == '1'):
            rascal.set_pin_high(66)
            rascal.set_pin_high(71)
            result = 'Pins set high'
        elif(request.params['target_state'] == '0'):
            rascal.set_pin_low(66)
            rascal.set_pin_low(71)
            result = 'Pins set low'
        else:
            result = 'Target_state is screwed up'
        return result 

    def write_serial(self):
        rascal.send_serial(request.params['serial_text'])
        return 'Text sent to serial port' 
