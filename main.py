from http.server import HTTPServer, BaseHTTPRequestHandler

CACHE_SERVER_PORT = 8090
CACHE_SERVER_ADDRESS = 'localhost'


class ServerCacheHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass

    def do_POST(self):
        pass


def run():
    server_url = (CACHE_SERVER_ADDRESS, CACHE_SERVER_PORT)
    http_start = HTTPServer(server_url, ServerCacheHandler)
    print("Server Started....  Running on Port:", CACHE_SERVER_PORT)
    http_start.serve_forever()


if __name__ == '__main__':
    run()
