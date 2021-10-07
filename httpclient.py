#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import os
import mimetypes

# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # Code (according to freetests.py) will just be the integer http response code
    def get_code(self, data):
        split_data = data.split("\r\n")
        split_status_line = split_data[0]
        status_code = split_status_line.split(" ")[1]
        return int(status_code)

    def get_headers(self,data):

        headers = ""
        split_data = data.split("\r\n")
        # Stop at newline carriage return
        carriage_newline = split_data.index("")
        for i in range(1, carriage_newline):
            headers += split_data[i]

    def get_body(self, data):
        split_data = data.split("\r\n")
        carriage_newline = split_data.index("")
        body = split_data[carriage_newline + 1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def remove_port_from_ip(self, host):
        new_hostname = ""
        if ":" in host:
            i = 0
            while i < len(host):
                if host[i] == ":":
                    i = len(host)
                else:
                    new_hostname += host[i]
                    i += 1
        else:
            new_hostname = host
        return new_hostname

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        host = self.remove_port_from_ip(parsed_url[1])
        
        if parsed_url.port == None:
            port = 80 # default for http
        else:
            port = parsed_url.port
        # fullpath will include the path (parsed_url[2]), along with all extra information (queries, fragments, etc.)
        full_path = ""
        for i in range(2,6):
            full_path += parsed_url[i]

        mimetype = ""
        if full_path == "/":
            mimetype = "text/html"
        else:
            mimetype = mimetypes.guess_type(host+full_path)
   
        # Assembling request start:
        # Start line
        request = f"GET {full_path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Accept: */*\r\n"
        #request += f"Accept: {mimetype}\r\n"
        request += f"Connection: close\r\n"
        request += "\r\n"

        #remote_ip = self.get_remote_ip()
        #print(f"full path: {full_path}")
        print(f"request: {request}")
        #print(f"url {url}")
        self.connect(host, port)
        self.sendall(request)

        #print(f"RECIEVED DATA : {self.recvall(self.socket)}")
        data = self.recvall(self.socket)
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        print(f"---DATA START---\n{data}\n---DATA END---\n")
        split = data.split("\r\n")
        #print(f"data split: =======START======={split}====END====")
        #print(f"index of NL CR: {split.index('')}")
        response_code = self.get_code(data)
        response_body = self.get_body(data)
        print("!!!~~~!~!~!~!~!!!~!~!~!!!~!~!~!~!~!~~~~~~~~~~~~~~~~~~~~~~")
        return HTTPResponse(response_code, response_body)
        
        # Accept any data given to us from a GET
        
        # Assembling request end.

        # random defaults/original code:
        # code = 500
        # body = ""
        # return HTTPResponse(code, body)
        pass

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
