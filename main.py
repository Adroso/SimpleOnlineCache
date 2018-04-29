from http.server import HTTPServer, BaseHTTPRequestHandler
import redis
import cgi
import json
import jsonschema

CACHE_SERVER_ADDRESS = 'localhost'
CACHE_SERVER_PORT = 8090

REDIS_HOST_ADDRESS = 'localhost'
REDIS_PORT = 6379

TIME_TO_LIVE = 30  # seconds

redis_server = redis.StrictRedis(host=REDIS_HOST_ADDRESS, port=REDIS_PORT, db=0)

class ServerCacheHandler(BaseHTTPRequestHandler):
    def validate_json(self, json_to_validate):
        desired_schema = {"type": "object",
                          "properties": {
                              "id": {"type": "number"},
                              "message": {"type": "string"}
                          }
                          }
        try:
            jsonschema.validate(json_to_validate, desired_schema)
            return True
        except jsonschema.ValidationError:
            return False

    def do_GET(self):
        path = str(self.path)
        if path.startswith('/messages'):
            document_id = path.split('/')[-1]
            if redis_server.exists(document_id):
                returning_data = redis_server.get(document_id)
                returning_data_package = json.loads(returning_data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(returning_data_package).encode("ASCII"))
            else:
                self.send_response(403, 'Resource not found')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(403, 'Resource not found')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()


    def do_POST(self):
        path = str(self.path)
        if path == '/messages':
            c_type, p_dict = cgi.parse_header(self.headers.get('Content-Type'))

            if c_type == 'application/json':
                data_len = int(self.headers.get('Content-Length'))
                incoming_data = self.rfile.read(data_len)
                loaded_data = json.loads(incoming_data)

                if not self.validate_json(loaded_data):
                    self.send_response(400, 'Bad Request, Document Malformed')
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()

                else:
                    redis_server.set(loaded_data['id'], json.dumps(loaded_data))
                    redis_server.expire(loaded_data['id'], TIME_TO_LIVE)

                    self.send_response(200)
                    self.end_headers()
            else:
                self.send_response(403, 'Resource not found')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        if path == '/clearcache':
            redis_server.flushall()




def run():
    server_url = (CACHE_SERVER_ADDRESS, CACHE_SERVER_PORT)
    http_start = HTTPServer(server_url, ServerCacheHandler)
    print("Server Started....  Running on Port:", CACHE_SERVER_PORT)
    http_start.serve_forever()


if __name__ == '__main__':
    run()
