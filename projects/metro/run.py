import sys
sys.path.insert(0, "./")

from projects.metro.unidir.server import server

server.port = 8521
server.launch() 