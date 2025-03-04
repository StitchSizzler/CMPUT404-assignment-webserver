#  coding: utf-8 
import socketserver
import os

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        if self.data.decode().split(' ')[0] != 'GET':
            self.send405NotAllowed()
            return

        path = self.data.decode().split(' ')[1]

        if path.startswith('/..') or len(path.split('/'))>3:
            self.send404NotFound()
            return

        if path[-1] == '/':
            if os.path.isdir('./www' + path):
                file = os.open('./www' + path + 'index.html', os.O_RDONLY)
                body = os.read(file, 1024).decode()
                self.send200Ok("html", body)
                return
            else:
                self.send404NotFound()
                return

        else:
            if os.path.isfile('./www' + path):
                file = os.open('./www' + path, os.O_RDONLY)
                body = os.read(file, 1024).decode()
                if path.split('/')[-1] == 'index.html':
                    self.send200Ok("html", body)
                    return
                else:
                    self.send200Ok("css", body)
                    return
            else:
                if os.path.isdir('./www' + path + '/'):
                    self.send301MovedPermanently()
                    return
                else:
                    self.send404NotFound()
                    return


    def send200Ok(self, type="html", content=""):
        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type:text/" + type + "\n\n" + content, "utf-8"))
        return

    def send301MovedPermanently(self):
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nContent-Type:text/html" + "\r\n", "utf-8"))
        return

    def send404NotFound(self):
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nContent-Type:text/html" + "\r\n", "utf-8"))
        return

    def send405NotAllowed(self):
        self.request.sendall(bytearray("HTTP/1.1 405 Not Allowed\r\nContent-Type:text/html" + "\r\n", "utf-8"))
        return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
