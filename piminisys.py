#!/usr/bin/python
#
# ^H> HucDuino 25-11-2018
# Raspberry, Python, Flask, PiMiniSys project
#

from flask import Flask, render_template
from datetime import datetime
import platform
import subprocess
import os
import psutil ## https://github.com/giampaolo/psutil / https://github.com/giampaolo/psutil/blob/master/INSTALL.rst ##
import vcgencmd ## https://github.com/nicmcd/vcgencmd ##

# edit you own settings
HOST = '0.0.0.0'               # flask server address (0.0.0.0 = all ip's)
PORT = 5000                    # flask server port
TITLE0 = '^H>'                 #
TITLE1 = 'HucDuino'            #
TITLE2 = 'PiMiniSys'           #
TITLE3 = '404'                 # title 404.html
TITLE4 = 'PiHardware'          # 
CONTENT = '10'                 # page refresh at sec.

# do not edit here under
app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/home')
@app.route('/piminisys')
def piminisys():
     return render_template("piminisys.html", title0=TITLE0, title1=TITLE1, title2=TITLE2, content=CONTENT,
                               diskUsageInfo=getDiskUsage(1), diskUsageHeader=getDiskUsage(0), upTime=getUptime(),
                               memoryUsageHeader=getMemoryUsage(0), memoryUsageInfo=getMemoryUsage(1), ipAddress=getIpAddress()[0],
                               memoryUsePercentage=round(float(getMemoryUsage(1)[2]) / float(getMemoryUsage(1)[1]), 4) * 100)

@app.route('/pihardware')
def pihardware():
     cpu_genric_info = cpu_generic_details()
     return render_template("pihardware.html", title0=TITLE0, title1=TITLE1, title4=TITLE4, content=CONTENT,
                               cpu_genric_info = cpu_genric_info)

def getDiskUsage(lineNumber):
	response = os.popen('df -h').readlines()
	return response[lineNumber].split()

def getMemoryUsage(lineNumber):
    response = os.popen('free -m').readlines()
    return response[lineNumber].split()

def getUptime():
    response = os.popen('cat /proc/uptime').readline().split()
    minutes = int(float(response[0])/60)
    time = [0, 0, 0]
    time[0] = int(minutes / 24 / 60) # get days
    time[1] = int(minutes /60 % 24) # get hours
    time[2] = minutes % 60 # get minutes
    return time

def getIpAddress():
    response = os.popen('hostname -I').readline()
    return response.split()

def cpu_generic_details():
    items = [s.split('\t: ') for s in subprocess.check_output(["cat /proc/cpuinfo  | grep 'model name\|Hardware\|Serial' | uniq "], shell=True).splitlines()]
    return items

@app.context_processor
def pi_model():
     pi_model = subprocess.check_output("cat /proc/device-tree/model | cut -d= -f2", shell=True)
     return dict(pi_model=pi_model)

@app.context_processor
def cpu_temperature():
     cpuTemp = float(subprocess.check_output(["vcgencmd measure_temp"], shell=True).split('=')[1].split('\'')[0])
     return dict(cpuTemp=cpuTemp)

@app.context_processor
def cpu_Percent():
     CPUp=psutil.cpu_percent(interval=1)
     return dict(CPUp=CPUp)

@app.context_processor
def sys_time():
	 sys_time = datetime.now().strftime("%H : %M : %S")
	 return dict(sys_time=sys_time)

@app.context_processor
def sys_date():
	 sys_data = datetime.now().strftime("%d %b %Y")
	 return dict(sys_data=sys_data)

@app.context_processor
def sys_year():
	 sys_year = datetime.now().strftime("%Y")
	 return dict(sys_year=sys_year)

@app.context_processor
def sys_name():
     sys_name =  platform.node()
     return dict(sys_name=sys_name)

@app.context_processor
def cpu_core_frequency():
     core_frequency = subprocess.check_output("vcgencmd get_config arm_freq | cut -d= -f2", shell=True).replace('\"', '')
     return dict(cpu_core_frequency=core_frequency)

@app.context_processor
def cpu_usage_info():
     item = {'in_use': 0}
     item['in_use'] = subprocess.check_output("top -b -n2 | grep 'Cpu(s)'|tail -n 1 | awk '{print $2 + $4 }'", shell=True)
     return dict(cpu_usage_info = item)

@app.context_processor
def cpu_processor_count():
     proc_info = subprocess.check_output("nproc", shell=True).replace('\"', '')
     return dict(cpu_processor_count=proc_info)

@app.context_processor
def cpu_core_volt():
     core_volt = subprocess.check_output("vcgencmd measure_volts| cut -d= -f2", shell=True).replace('\"', '')
     return dict(cpu_core_volt=core_volt)

@app.errorhandler(404)
def page_not_found(e):
      return render_template('404.html', title0=TITLE0, title1=TITLE1, title3=TITLE3), 404

if __name__ == "__main__":
     app.run(host=HOST, port=PORT, debug=True)
