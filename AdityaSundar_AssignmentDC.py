#Aditya Sundar
#adisun@umich.edu
#5 May 2022

import asyncio,time

r1,r2,rl=0,100*1000,30*1000     #resistances in ohms
vs=10                           #voltage source
countv,counta=0,0
delta_v,delta_a,delta_r=0.1,0.3,1         #time intervals to record voltage and current

class circuit():
    async def f1(self,host,*arg):
        t=time.time()-start
        self.timestamp=round(t,3)
        r1t=r1+t/10*100*1000
        r2t=r2-t/10*100*1000
        It=vs/(r1t+r2t*rl/(r2t+rl))
        vt=vs-It*r1t
        Iam=It-vt/r2t
        self.current=round(Iam,6)
        self.voltage=round(vt,6)

c=circuit()

class voltmeter():
    async def f2(self,url,*args):
        self.value=c.voltage
        self.tvolt=time.time()
        print('Time=',round(self.tvolt-start,3),'s, Voltage=',self.value,' V')

v=voltmeter()

class ammeter():
    async def f2(self,url,*args):
        self.value=c.current
        self.tamm=time.time()
        print('Time=',round(self.tamm-start,3),'s, Current=',self.value,' A')

a=ammeter()

class ohmeter():
    def __init__(self):
        self.resistances=[]
        self.timestamps=[]
    async def f2(self,url,*args):
        if (c.timestamp%1)<0.1 or (c.timestamp%1)>0.9:
            print('Time=',c.timestamp,'s, Resistance_L=',round(v.value/a.value/1000,3),' k Ohm')
            print('---------------------------------------------------------------------------')
    
class rolling(ohmeter):
    def __init__(self):
        super().__init__()
        self.average=0


o=ohmeter()
oroll=rolling()

#following block of code inspired from https://stackoverflow.com/questions/53339921/asyncio-run-two-different-functions-periodically-with-different-intervals

async def measurement(freq, device, *args):
    while True:
        t1 = time.time()
        await device(*args)
        elapsed = time.time() - t1
        await asyncio.sleep(freq - elapsed)
        if abs(c.timestamp-int(c.timestamp/delta_v)*delta_v)<0.01:
            oroll.resistances.append(v.value/a.value)   #storing all resistance updates in a ohmeter class attribute
            oroll.timestamps.append(c.timestamp)        #storing all timestamps in a ohmeter class attribute
            num=len([i for i in oroll.timestamps if i>oroll.timestamps[-1]-2])
            oroll.average=round(sum(oroll.resistances[-1:])/len(oroll.resistances[-1:])/1000,3)  #compute rolling average over last 2 seconds
            print('*** Rolling average of Resistance_L=',oroll.average,' k ohm')
        if time.time()-start>10.02:
            loop.stop()

start=time.time()
loop = asyncio.get_event_loop()
loop.create_task(measurement(0.01,c.f1,'circuit'))     #circuit class called every 0.01 s
loop.create_task(measurement(delta_v,v.f2,'voltmeter'))  #voltmeter class called every delta_v seconds
loop.create_task(measurement(delta_a,a.f2,'ammeter'))   #ammeter class called every delta_a seconds
loop.create_task(measurement(delta_r,o.f2,'ohmeter'))   #ohmeter class called every delta_r second
loop.run_forever()
