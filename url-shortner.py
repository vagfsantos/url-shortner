from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import requests

form = '''
  <form action="/" method="POST">
    <label>
      <span>URL</span>
      <input type="text" name="url">
    </label>
    <label>
      <span>Short URL</span>
      <input type="text" name="short_url">
    </label>

    <button>Short it now</button>
  </form>
  {}
'''

saved_urls = {}


def get_url_links():
    new_url_array = []
    for short_url in saved_urls:
        link = '''
          <a href={}>{}<a/>
        '''.format("http://localhost:8000?url={}".format(short_url), short_url)

        new_url_array.append(link)

    return new_url_array


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urlparse(self.path)

        if(params):
            parsed_params = parse_qs(params[4])
            url = parsed_params.get('url')

            if(url):
                redirect_url = saved_urls[url[0]]
                self.send_response(303)
                self.send_header("Location", redirect_url)
                self.end_headers()
                return None

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(form.format('\n'.join(get_url_links())).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = parse_qs(self.rfile.read(content_length).decode())

        url = body.get("url")[0]
        short_url = body.get("short_url")[0]

        if(content_length == 0 or not url or not short_url or not self.is_url_valid(url)):
            self.send_response(400)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Not Found".encode())
            return None

        saved_urls[short_url] = url

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def is_url_valid(self, url):
        try:
            req = requests.get(url)
            if req.status_code == 404:
                return False
            else:
                return True
        except:
            return False


app = HTTPServer(('', 8000), AppHandler)
app.serve_forever()
