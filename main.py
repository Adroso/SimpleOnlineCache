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

    def send_403(self):
        self.send_response(403, 'Resource not found')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def send_200(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def validate_json(self, json_to_validate):
        """Verifies if a json is of a desired schema and returns True of False depending on outcome."""
        desired_schema = {"type": "object",
                          "properties": {
                              "id": {"type": "number"},
                              "message": {"type": "string"}}}
        try:
            jsonschema.validate(json_to_validate, desired_schema)
            return True
        except jsonschema.ValidationError:
            return False

    def do_GET(self):
        """Method called on GET request, only handles if request is to /messages otherwise returns 403"""
        path = str(self.path)
        if path.startswith('/messages'):
            document_id = path.split('/')[-1]
            if redis_server.exists(document_id):
                returning_data = redis_server.get(document_id)
                returning_data_package = json.loads(returning_data)
                self.send_200()
                self.wfile.write(json.dumps(returning_data_package).encode("ASCII"))
            else:
                self.send_403()
        else:
            self.send_403()


    def do_POST(self):
        """Method called on POST, includes handling of input to /messages, ability to clear cache through /clearcache
           And set a new TTL while server is running.
        """
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
                    self.send_200()
            else:
                self.send_403()

        elif path == '/clearcache':  # clears all records in redis cache
            redis_server.flushall()
            self.send_200()

        elif path.startswith('/ttl'):  # used to adjust the future TTL on post documents
            new_ttl = int(path.split('/')[-1])
            # TODO set dynamic TTL

        else:
            self.send_403()


def run():
    server_url = (CACHE_SERVER_ADDRESS, CACHE_SERVER_PORT)
    http_start = HTTPServer(server_url, ServerCacheHandler)
    print("Server Started....  Running on Port:", CACHE_SERVER_PORT)
    http_start.serve_forever()


if __name__ == '__main__':
    run()
