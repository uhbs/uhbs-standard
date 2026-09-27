import json
import sys


class HandlerManager:
    def __init__(self, config):
        self.config = config

    def handle(self, data):
        try:
            print(json.dumps(data, default=str), file=sys.stderr)
        except Exception:
            print(str(data), file=sys.stderr)
