import telnetlib
import time, datetime, re, sys, os, argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
###Notes from Felica###
#b'+9.90000000E+37\r\n'
#+9.90000000E+37
#This is the open circuit value for any measurements
#Set multimeter to DHCP and hard reset.
#Might have to change the IP to closer to your computer IP.


def get_error(multimeter):
    multimeter.write(("SYST:ERR?\n").encode('ascii'))
    time.sleep(0.2)
    value= multimeter.read_eager()
    # value = value.decode("ascii")
    # value = re.search(r'\d.{13}', value)
    if value !=b'+0,"No error"\r\n' and value != b'':
        print(value)
        return(True)

def collect(ip="10.30.128.63", show=False, save=True, fname="test.csv",delay=1,v=True):
    multimeter_address = ip
    #setup telnet
    multimeter = telnetlib.Telnet()
    #initialize the multimeter with the given settings
    multimeter.open(multimeter_address,port=3490,timeout=3)
    #set the multimeter into remote mode
    multimeter.write(("SYST:REM\n").encode('ascii'))
    multimeter.write(("*CLS\n").encode('ascii'))
    multimeter.write(("disp off\n").encode('ascii'))
    multimeter.write(("conf:res\n").encode('ascii'))
    multimeter.write(("syst:beep:state off\n").encode('ascii'))

    start=time.time()
    voltage=[0]
    t=[0]

    if show:
        fig=plt.figure()
        line,=plt.plot(t,voltage,'ro-')
    print('start :  {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    print(start)

    def update(delay):
        multimeter.write(("MEAS:RES?\n").encode("ascii"))

        value= multimeter.read_eager()
        time.sleep(delay)
        #get_error(multimeter)
        #print(value)
        value = value.decode("ascii")
        value = re.search(r'\d.{13}', value)

        # print(type(float(value)))
        try:
            if value==None:
                #checks for an unmatching string, usually ''
                pass
            elif float(value.group(0))>1e37:
                pass
            else:
                #print(value.group(0),time.time()-start)
                v=float(value.group(0))
                dt=time.time()-start
                voltage.append(v)
                t.append(dt)
                if v:
                    print(v,dt)
        except Exception as e:
            print("couldnt append data values:\n",e)
        #print(voltage,t)
        if show:
            line.set_data(t,voltage)
            plt.xlim(0, max(t)*1.1)
            plt.ylim(0, max(voltage)*1.1)
            return line,




    if show:
        try:
            line_ani = animation.FuncAnimation(fig, update, interval=1000)
            plt.show()
        except KeyboardInterrupt:
            multimeter.close()
    else:
        while True:
            try:
                update(delay)
                if v:
                    print("step")
            except Exception as e:
                print("meter error",get_error(multimeter))
                print(e)
                break
    print('end   :  {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    #closes the multimeter
    multimeter.close()
    if save:
        data=np.array([voltage[1:],t[1:]]).T

        np.savetxt(fname, data,header="R,t",delimiter=',')

if __name__=="__main__":
    parser = argparse.ArgumentParser( formatter_class=argparse.RawDescriptionHelpFormatter, description="Measure the resistance over time of a sample conected to to a DMM4040 or equivalent")
    parser.add_argument("save",type=str,help="the filename to save as")

    parser.add_argument("--ip", type=str,help="the ip address of the multimeter")
    parser.add_argument("--delay", type=int,help="the time delay between measurements")
    parser.add_argument("--show", action="store_true",help="display graph in real time")
    parser.add_argument("-v", "--verbose", action="store_true",default=False,help="print values to stdout for each measurement")
    args = parser.parse_args()
    collect(ip=args.ip,fname=args.save,v=args.verbose,show=args.show,delay=args.delay)
