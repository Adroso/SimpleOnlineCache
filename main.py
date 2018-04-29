from http.server import HTTPServer, BaseHTTPRequestHandler
import redis
import cgi
import json

CACHE_SERVER_ADDRESS = 'localhost'
CACHE_SERVER_PORT = 8090

REDIS_HOST_ADDRESS = 'localhost'
REDIS_PORT = 6379

redis_server = redis.StrictRedis(host=REDIS_HOST_ADDRESS, port=REDIS_PORT, db=0)

class ServerCacheHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass

    def do_POST(self):
        path = str(self.path)
        if path == '/messages':
            c_type, p_dict = cgi.parse_header(self.headers.get('Content-Type'))

            if c_type == 'application/json':
                data_len = int(self.headers.get('Content-Length'))
                incoming_data = self.rfile.read(data_len)
                loaded_data = json.loads(incoming_data)


def run():
    server_url = (CACHE_SERVER_ADDRESS, CACHE_SERVER_PORT)
    http_start = HTTPServer(server_url, ServerCacheHandler)
    print("Server Started....  Running on Port:", CACHE_SERVER_PORT)
    http_start.serve_forever()


if __name__ == '__main__':
    run()
