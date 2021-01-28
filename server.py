#  coding: utf-8 
import socketserver, re, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

HOST, PORT = "127.0.0.1", 8080
class MyWebServer(socketserver.BaseRequestHandler):

    def serve(self,header,body):
        self.request.send(header.format(len(body)).encode("utf-8"))
        self.request.send(body.encode("utf-8"))

    def get_allowed(self,rootname):
        allowed = [rootname]
        for root, dirs, files in os.walk(rootname, topdown=False):
            for name in files: allowed.append(os.path.join(root, name))
            for name in dirs: allowed.append(os.path.join(root, name))
        return allowed

    def handle(self):
        self.url = "http://{0}:{1}".format(HOST,PORT)
        self.data = self.request.recv(1024).strip()

        root = "www"
        success_header = 'HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: {}\r\n\r\n'

        not_found_header = 'HTTP/1.1 404 Not found\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'
        not_found_body = "<html><head><title>404</title></head><body><p>404 page not found</p></body></html>"

        redirect_header = 'HTTP/1.1 301 Moved Permanently\r\nLocation: %s\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'
        redirect_body = "<html><head><title>301</title></head><body><p>The page you requested has been moved:</p><a href=\"%s\">here</a></body></html>"

        not_allowed_header = 'HTTP/1.1 405 Not allowed\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'
        not_allowed_body = "<html><head><title>405</title></head><body><p>405 Not allowed</p></body></html>"

        print ("Got a request of: %s\n" % self.data)
        data = self.data.decode()
        response = re.findall("(?<=GET )(.*)(?= HTTP)",data)
        allowed = self.get_allowed(root+"/")
        if len(response) == 0: # regex cannot find 'GET' in response, therefore serve 405 response
             self.serve(not_allowed_header, not_allowed_body)
        else:
            path = response[0]
            fullpath = root + path
            print(os.path.abspath(fullpath))
            if os.path.exists(fullpath): # Abspath for directory checking?
                try:
                    with open(fullpath,"r") as f: self.serve(success_header % ("text/css" if ".css" in path else "text/html"),f.read())
                except IsADirectoryError:
                    if path[-1] == "/":
                        with open(fullpath+"index.html","r") as f: self.serve(success_header,f.read())
                    else:
                        self.serve(redirect_header % (self.url+path+"/"), redirect_body % (self.url+path+"/"))
            else: self.serve(not_found_header,not_found_body)

if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
