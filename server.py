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

HOST, PORT = "localhost", 8080

class MyWebServer(socketserver.BaseRequestHandler):

    def serve(self,header,body):
        self.request.send(header.format(len(body)).encode("utf-8"))
        self.request.send(body.encode("utf-8"))

    def handle(self):
        self.url = "http://{0}:{1}/".format(HOST,PORT)
        self.data = self.request.recv(1024).strip()

        root = "www/"
        success_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'

        not_found_header = 'HTTP/1.1 404 Not found\r\nContent-Length: {}\r\n\r\n'
        not_found_body = "404 Not Found"

        print ("Got a request of: %s\n" % self.data)
        data = self.data.decode()
        filepath = re.findall("(?<=GET /)(.*)(?= HTTP)",data)[0]
        print(root+filepath)
        if os.path.exists(root+filepath):
            try:
                with open(root+filepath,"r") as f: self.serve(success_header,f.read())
            except IsADirectoryError:
                with open(root+filepath+"index.html","r") as f: self.serve(success_header,f.read())
        else: self.serve(not_found_header,not_found_body)

if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
