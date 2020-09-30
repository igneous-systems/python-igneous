import json
import typing
import requests

from .util import empty
from .response import Response


class Request:

    def __init__(self, client: 'Client', method: str, path: str,
                 json_filter: typing.Optional[typing.Callable] = None, **options):
        """

        :param method: "get" or "post" or "put" etc.
        :param path:
        :param kwargs:
        """
        self.client = client
        self.dry_run = client.dry_run
        self.method: str = method
        self.path: str = path
        self.json_filter: typing.Optional[typing.Callable] = json_filter
        self.options: dict = options
        self.options.setdefault('headers', {})
        if not empty(self.client.api_key):
            self.headers.setdefault('Authorization', self.client.api_key)
        if 'json' in self.options:
            self.headers.setdefault('Content-Type', 'application/json')

    @property
    def url(self) -> str:
        return self.client.scheme + "://" + self.client.api_server + self.client.api_base_path + self.path

    def to_dict(self) -> dict:
        d = dict(url=self.url, method=self.method, headers=self.headers, payload=self.options.get('json', None))
        if self.dry_run:
            d['dryRun'] = True
        return d

    @property
    def headers(self) -> dict:
        return self.options['headers']

    def __str__(self):
        request_str = f'{self.method.upper()} {self.url}\n' + '\n'.join([f"{k}:{v}" for k, v in self.headers.items()])
        if 'json' in self.options:
            request_str += json.dumps(self.options['json'], sort_keys=True, indent=4)
        return request_str + '\n'

    def run(self) -> Response:
        func = getattr(requests, self.method)
        response = Response(self)
        if self.dry_run:
            response.error = Exception('dry run')
        else:
            try:
                response.response = func(self.url, **self.options)
            except Exception as e:
                response.error = e
        return response
