#!/usr/bin/env python
"""
Threaded Python TCP Ping Test (defaults to port 80, 3 packets)
Usage: ./tcpping.py host [port] [maxCount]
- Ctrl-C Exits 
Derived from
  Jonathan Yantis, Blade.            https://github.com/yantisj/tcpping/blob/master/tcpping.py
  Andrey Belykh, Dundas Software.    https://stackoverflow.com/questions/48009669/using-for-python-tcp-ping-time-measure-difference-from-other-tools
TODO:
   Jim Willie, Akamai Technologies.  https://github.com/jwyllie83/tcpping
"""

import sys
import os
import errno
import socket
import time
import signal
from timeit import default_timer as timer
import threading

host = ''
port = 80
#Optionally qualify underlying machine
#a = time.clock()
#time.sleep(2)
#b = time.clock()
#print(b-a)
# Default to 10000 connections max
maxCount = 3
count = 0
connTo = 1
intergreen = 0.05
proto = 6            #https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
                     #https://tools.ietf.org/html/rfc793

## Inputs

# Required
try:
    host = sys.argv[1]
except IndexError:
    sys.stderr.write("Usage: tcpping.py host [port] [maxCount]\n")
    sys.exit(1)

# Optional
try:
    port = int(sys.argv[2])
except ValueError:
    sys.stderr.write("Error: Port Must be Integer: ")
    sys.stderr.write(sys.argv[2])
    sys.stderr.write("\n")
    sys.exit(1)
except IndexError:
    pass

try:
    maxCount = int(sys.argv[3])
except ValueError:
    sys.stderr.write("Error: Max Count Value Must be Integer ")
    sys.stderr.write(sys.argv[3])
    sys.stderr.write("\n")
    sys.exit(1)
except IndexError:
    pass

# Pass/Fail counters
passed = 0
failed = 0

def getResults():
    """ Summarize Results """

    lRate = 0
    if failed != 0:
        lRate = failed / (count) * 100
        lRate = "%.2f" % lRate

    #print("\nTCP Ping Results: Connections (Total/Pass/Fail): [{:}/{:}/{:}] (Failed: {:}%)".format((count), passed, failed, str(lRate)))

def signal_handler(signal, frame):
    """ Catch Ctrl-C and Exit """
    #getResults()
    sys.exit(0)

# Register SIGINT Handler
signal.signal(signal.SIGINT, signal_handler)

# Loop while less than max count or until Ctrl-C caught
while count < maxCount:

    # Increment Counter
    count += 1

    success = False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 1sec Timeout
    s.settimeout(1)

    # Try to Connect
    try:
      t = threading.Thread(target=s.connect((host, int(port))))
      s_start = timer()
      t.start()                                      #do thread
      s_stop = timer()
      s.shutdown(socket.SHUT_RD)
      success = True
      s.close()

    except socket.timeout as e:
      s.close()
      sys.stderr.write("Connection timed out!\n")
      print("%s,%s,%s,%s,%s" % (host, port, proto, (count-1), 9999))
      failed += 1
    except socket.gaierror as (eno,estr):
      #https://docs.python.org/3/library/socket.html#socket.socket.connect
      s.close()
      sys.stderr.write(estr)
      sys.stderr.write("\n")
      print("%s,%s,%s,%s,%s" % (host, port, proto, (count-1), 9999))
      failed += 1
    except socket.error as e:
      #https://docs.python.org/2/library/errno.html
      s.close()
      sys.stderr.write("Socket Error!\n")
      print("%s,%s,%s,%s,%s" % (host, port, proto, (count-1), 9999))
      failed += 1
      if e.errno == errno.ECONNREFUSED or e.errno==errno.EHOSTUNREACH:
        sys.stderr.write(os.strerror(e.errno))
        sys.stderr.write("\n")
      else:
        raise
    except OSError as e:
      s.close()
      sys.stderr.write("OS Error:\n")
      sys.stderr.write(os.strerror(e.errno))
      sys.stderr.write("\n")
      print("%s,%s,%s,%s,%s" % (host, port, proto, (count-1), 9999))
      failed += 1

    if success:
      s_runtime = "%.3f" % (1000 * (s_stop - s_start))
      #print("Connected to %s[%s]: tcp_seq=%s time=%s ms" % (host, port, (count-1), s_runtime))
      print("%s,%s,%s,%s,%s" % (host, port, proto, (count-1), s_runtime))
      passed += 1

    # intergreen rest
    if count < maxCount:
        time.sleep(intergreen)

# Output Results if maxCount reached
#getResults()
