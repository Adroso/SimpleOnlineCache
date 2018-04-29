from http.server import HTTPServer, BaseHTTPRequestHandler
import redis

CACHE_SERVER_ADDRESS = 'localhost'
CACHE_SERVER_PORT = 8090

REDIS_HOST_ADDRESS = 'localhost'
REDIS_PORT = 6379

redis_server = redis.StrictRedis(host=REDIS_HOST_ADDRESS, port=REDIS_PORT, db=0)

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
