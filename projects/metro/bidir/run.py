import sys
sys.path.insert(0, "./")

from projects.metro.bidir.server import server

server.port = 8521
server.launch() 