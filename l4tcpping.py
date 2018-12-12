 #!/usr/bin/env python
"""
Threaded Python TCP Ping Test (defaults to port 80, 10000 packets)

Usage: ./tcpping.py host [port] [maxCount] [ConnectionTimeout] [ConnectionIntergreenRest]
- Ctrl-C Exits with Results

Derived from
  Jonathan Yantis, Blade.             https://github.com/yantisj/tcpping/blob/master/tcpping.py
  Andrey Belykh, 	Dundas Software.    https://stackoverflow.com/questions/48009669/using-for-python-tcp-ping-time-measure-difference-from-other-tools
"""

import sys
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
maxCount = 10000 
count = 0
connTo = 1
intergreen = 1

## Inputs

# Required
try:
    host = sys.argv[1]
except IndexError:
    print("Usage: tcpping.py host [port] [maxCount]")
    sys.exit(1)

# Optional
try:
    port = int(sys.argv[2])
except ValueError:
    print("Error: Port Must be Integer:", sys.argv[3])
    sys.exit(1)
except IndexError:
    pass

try:
    maxCount = int(sys.argv[3])
except ValueError:
    print("Error: Max Count Value Must be Integer", sys.argv[3])
    sys.exit(1)
except IndexError:
    pass

try:
    connTo  = int(sys.argv[4])
except ValueError:
    print("Error: Max Connection Timeout Value Must be Integer", sys.argv[4])
    sys.exit(1)
except IndexError:
    pass

try:
    intergreen  = int(sys.argv[5])
except ValueError:
    print("Error: Connection intergreen rest must be Integer", sys.argv[5])
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

    print("\nTCP Ping Results: Connections (Total/Pass/Fail): [{:}/{:}/{:}] (Failed: {:}%)".format((count), passed, failed, str(lRate)))

def signal_handler(signal, frame):
    """ Catch Ctrl-C and Exit """
    getResults()
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

    except socket.timeout:
        print("Connection timed out!")
        failed += 1
    except OSError as e:
        print("OS Error:", e)
        failed += 1   

    if success:
      s_runtime = "%.2f" % (1000 * (s_stop - s_start))
      print("Connected to %s[%s]: tcp_seq=%s time=%s ms" % (host, port, (count-1), s_runtime))
      passed += 1

    # intergreen rest
    if count < maxCount:
        time.sleep(intergreen)

# Output Results if maxCount reached
getResults()
