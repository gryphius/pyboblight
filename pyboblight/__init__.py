import socket
import time
import random


class BobCLient(object):
    def __init__(self,host='127.0.0.1',port=19333):
        self.host=host
        self.port=port
    
        self.lights={}
        
        self.priority=128
        """priority over other boblight clients"""
        
        self.file=None
        self.sock=None
        
        self.socketerror=False
        self.do_debug=False
        self.handshake()
        
    def debug(self,msg):
        if not self.do_debug:
            return
        print msg
        
    def send_command(self,command):
        if not self.is_connected():
            self.reconnect()
        
        self.debug("SND: %s"%command)
        try:
            self.sock.send(command)
            self.sock.sendall('\r\n')
        except:
            self.socketerror=True
    
    def readline(self):
        try:
            msg=self.file.readline().strip()
            self.debug("RCV: %s"%msg)
            return msg
        except:
            self.socketerror=True
            return None
        
    def _sync(self):
        self.send_command('sync')
        
    def _prepare_rgb_color(self,lightname,r,g,b):
        fr=r/255.0
        fg=g/255.0
        fb=b/255.0
        self.send_command("set light %s rgb %s %s %s"%(lightname,fr,fg,fb))
    
    def _create_socket(self):
        return socket.create_connection((self.host, self.port))
        
    def reconnect(self):
        self.sock = self._create_socket()
        self.file = self.sock.makefile('rw')
        self.socketerror=False
        
    
    def disconnect(self):
        try:
            self.send_command('quit')
            self.sock.close()
        except:
            pass
        self.sock=None
        self.file=None
        
    
    def is_connected(self):
        if self.sock == None or self.socketerror:
            return False
        return True
    
    def refresh_lights_info(self):
        self.send_command("get lights")
        ans=self.readline().split()
        assert len(ans)==2
        assert ans[0]=='lights',"Expected 'lights <num>' but got '%s'"%ans
        nlights=int(ans[1])
        
        tempdic={}
        for i in range(nlights):
            linfo=self.readline().split()
            assert len(linfo)==7
            assert linfo[0]=='light'
            assert linfo[2]=='scan'
            kw1,name,kw2,vmin,vmax,hmin,hmax=linfo
            l=Light(name, self)
            l.hmin=hmin
            l.hmax=hmax
            l.vmin=vmin
            l.vmax=vmax
            tempdic[name]=l
        self.lights=tempdic
        
    
    def handshake(self):
        if not self.is_connected():
            self.reconnect()
        self.send_command('hello')
        ret=self.readline()
        if ret!='hello':
            raise Exception("hello failed")
        self.send_command("set priority %s"%self.priority)
        
        #refresh server info
        if self.get_num_lights()==0:
            self.refresh_lights_info()
            
        
    def get_num_lights(self):
        return len(self.lights)


    def update(self):
        """sent current light state to server"""
        for k,light in self.lights.iteritems():
            self._prepare_rgb_color(light.name, light.r, light.g, light.b)
        self._sync()
    
class Light(object):
    """Represents a single light"""
    
    def __init__(self,name,client):
        self.client=client
        self.name=name
        self.hmin=0
        self.hmax=100
        self.vmin=0
        self.vmax=100
        
        self.r=0
        self.g=0
        self.b=0
        

    def set_color(self,r,g,b):
        self.r=r
        self.g=g
        self.b=b
        
    def __str__(self):
        return """<Light name='%s' hscan='%s-%s' vscan='%s-%s' color='%s/%s/%s'>"""%(self.name,self.hmin,self.hmax,self.vmin,self.vmax,self.r,self.g,self.b)
    
    
    def __repr__(self):
        return str(self)
    
if __name__=='__main__':
    #initialize
    client=BobCLient('192.168.23.56')
    
    #print light information
    print client.lights
    
    #send random colors for 20 seconds
    now=time.time()
    stop=now+20
    while time.time()<stop:
        time.sleep(0.1)
        #prepare the light color changes
        for name,light in client.lights.iteritems():
            light.set_color(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        #tell the client to update the current light color state on the server
        client.update()
