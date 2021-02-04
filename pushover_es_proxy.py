#!/usr/bin/env python

import os
import json
import requests 
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer


# Environment Variables
# BIND_IP - The IP this proxy will listen on
# BIND_PORT - The port this proxy will listen on
# AUTH_TOKEN - Base64 encoded username and password in the format of `username:password` that will be included with the alert
# USER - The Pushover username this proxy will send to
# TOKEN - The Pushover application token this proxy will send to

BIND_IP = os.environ.get('BIND_IP', '0.0.0.0')
BIND_PORT = os.environ.get('BIND_PORT', 8080)
AUTH_TOKEN = os.environ['AUTH_TOKEN']

URL = "https://api.pushover.net/1/messages.json"
USER = os.environ['USER']
TOKEN = os.environ['TOKEN']

telemetry = {
  "health_requests": 0,
  "200_requests": 0,
  "401_requests": 0,
  "599_requests": 0
}

def get_content_length(headers):
  for header_key,header_value in headers.items():
      if header_key.lower() == 'content-length':
        return int(header_value)
  return 0

class RequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    telemetry['health_requests'] += 1
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(telemetry).encode())
    return RequestHandler

  def do_POST(self):
    try:

      # Make sure the request is authenticated
      if self.headers["Authorization"] != f"Basic {AUTH_TOKEN}":
        telemetry['401_requests'] += 1
        self.send_response(401)
        return RequestHandler

      # Load the message body sent from Kibana/Elasticsearch
      message = self.rfile.read(get_content_length(self.headers))
              
      # Parse the data into the params field
      PARAMS = {
        'user':USER,
        'token':TOKEN,
        'message':message
      } 
      
      # sending get request and saving the response as response object 
      response = requests.post(url = URL, params = PARAMS)
      
      # Return whatever response pushover gave us
      telemetry['200_requests'] += 1
      self.send_response(response.status_code)
      # Return the appropriate content type header
      if response.headers.get("Content-type"):
        self.send_header("Content-type", response.headers.get("Content-type"))
        self.end_headers()
      # Return the body if it exists
      if len(response.text) > 0:
        self.wfile.write(response.text.encode())
      return RequestHandler

    except Exception as error:
      traceback.print_exc()
      telemetry['599_requests'] += 1
      self.send_response(599)
      return RequestHandler

def main():
  print(f"Listening on {BIND_IP}:{BIND_PORT}")
  server = HTTPServer((BIND_IP, int(BIND_PORT)), RequestHandler)
  server.serve_forever()

if __name__ == "__main__":
  main()
