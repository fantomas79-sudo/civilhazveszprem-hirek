import http.server, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(('localhost', 5501), handler)
print('Serving on http://localhost:5501')
httpd.serve_forever()
