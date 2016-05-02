import sys
from shipy.dpyexec import Shipy

shipy_client = Shipy()
shipy_client.dpy(sys.argv[1:])
