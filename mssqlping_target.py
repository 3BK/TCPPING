#!/usr/bin/python

import subprocess
import re
import os,sys,logging
from time import localtime,strftime
import time

if os.name == 'nt':
  splunk_home = '_some_path_'
  python_bin = '_some_path_\python.exe'
else:
  python_bin = '/usr/bin/python'

indexTime = "[" + strftime("%m/%d/%Y %H:%M:%S %p %Z",localtime()) + "]"

print ("time,server,user,bk_sent,bk_received,bk_lost,bk_minimum,bk_maximum,bk_average,bk_down,bk_target,bk_port,bk_error")
bk_sent=""
bk_received=""
bk_lost=""
bk_minimum=""
bk_maximum=""
bk_average=""
bk_target=""
bk_port=""
try:
  bk_step=0
  reg="TCP connect statistics for [0-9]*.[0-9]*.[0-9]*.[0-9]*:[0-9]*:"
  p = subprocess.Popen(["some_stub"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
  for line in iter(p.stdout.readline, b''):
    if bk_step==2:
      ml = re.search(reg, line)
      if ml:
        x = line.split()
        bk_minimum=x[2][:len(x[2])-3]
        bk_maximum=x[5][:len(x[5])-3]
        bk_average=x[8][:len(x[8])-2]
        bk_step=3
    if bk_step==1:
      ml = re.search(reg, line)
      if ml:
        #print ("step1")
        x = line.split()
        bk_sent=x[2][:len(x[2])-1]
        bk_received=x[5][:len(x[5])-1]
        bk_lost=x[8]
        reg="Minimum = [0-9]*\.[0-9]*ms, Maximum = [0-9]*\.[0-9]*ms, Average = [0-9]*\.[0-9]*ms"
        bk_step=2
    if bk_step==0:
      ml = re.search(reg, line)
      if ml:
        foo=line.split()
        y=foo[4].split(":")
        bk_port=y[1]
        bk_target=y[0]
        reg="  Sent = [0-9]*, Received = [0-3], Lost = [0-3] .*,"
        bk_step=1

  print ("%s,some_fqdn_host.on.ca,mssqlping,%s,%s,%s,%s,%s,%s,0,%s,%s," % (indexTime,bk_sent,bk_received,bk_lost,bk_minimum,bk_maximum,bk_average,bk_target,bk_port))

except Exception as e:
  print ("%s,some_fqdn_host,mssqlping,,,,,,,1,some_fqdn_target,1433,%s" %(indexTime,e))
