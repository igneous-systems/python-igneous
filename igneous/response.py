import typing
import requests
import json


class Undefined(object):
    def __str__(self):
        return "<undefined>"


undefined = Undefined()


class Response:
    def __init__(self, request: 'Request'):
        self.request: 'Request' = request
        self.error: typing.Optional[Exception] = None
        self.response: typing.Optional[requests.Response] = None
        self._data = undefined

    @property
    def ok(self) -> bool:
        return self.response.ok if self.response is not None else False

    @property
    def data(self) -> typing.Optional[dict]:
        if self._data is undefined:
            if self.response is not None and callable(self.response.json):
                try:
                    self._data = self.response.json()
                except json.decoder.JSONDecodeError:
                    self._data = None
            else:
                self._data = None
        return self._data

    @property
    def has_data(self) -> bool:
        return self.data is not None

    def to_dict(self) -> dict:
        d = dict(
            request=self.request.to_dict(),
            reason=None,
            code=0,
            data=self.data,
            ok=self.ok
        )
        if self.error is not None:
            d['reason'] = str(self.error)
            d['code'] = 503  # service unavailable
        elif self.response is not None:
            d['reason'] = self.response.reason
            d['code'] = self.response.status_code
        return d
