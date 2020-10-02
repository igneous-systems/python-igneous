"""
The Client class to use to make all Igneous API calls
"""

import typing
import re
from .request import Request

from .util import empty


class Client:
    """REST Client to communicate with Igneous Endpoints.
    """
    API_SERVER = '127.0.0.1'
    API_KEY = None
    SCHEME = 'http'
    API_BASE_PATH = '/x/igneous'

    def __init__(self, api_server=None, api_key=None, scheme=None, api_base_path=None, dry_run=False, api_version=None):
        self.api_server: str = Client.API_SERVER if empty(api_server) else api_server
        self.api_key: typing.Optional[str] = Client.API_KEY if empty(api_key) else api_key
        self.scheme: str = Client.SCHEME if empty(scheme) else scheme
        self.api_base_path: str = Client.API_BASE_PATH if empty(api_base_path) else api_base_path
        self.dry_run: bool = dry_run
        self.api_version: str = "v1" if empty(api_version) else api_version

    def _path(self, *args):
        p = '/' + self.api_version
        for a in args:
            if a is None:
                continue  # replace None with empty string
            p += str(a)
        return p

    def get(self, path):
        return Request(self, 'get', self._path(path)).run().to_dict()

    def get_version(self) -> dict:
        """Retrieve version from server
        """
        return Request(self, 'get', '/version').run().to_dict()

    def buckets_get(self, system_name: str = '', bucket_name: str = '', **kwargs) -> dict:
        """Retrieve buckets

        :param system_name: if given, retrieve info for buckets from that system only
        :param bucket_name: if given, retrieve info for that bucket only
        :param kwargs: extra params for client.get call
        :return:
        """
        params = {} if empty(system_name) else {'system': system_name}
        response = Request(self, 'get', self._path('/buckets/', bucket_name), params=params, **kwargs).run()
        return response.to_dict()

    def buckets_list(self, system_name: str = '', match: str = '', names_only: bool = False, **kwargs) -> dict:
        r = self.buckets_get(system_name=system_name, bucket_name='', **kwargs)
        if not r['ok']:
            return r
        if match is not None and match != '' and r.get('data') is not None:
            buckets = r['data'].get('Buckets', {})
            filtered = {}
            for bucket_name, bucket in buckets.items():
                if re.search(match, bucket_name):
                    filtered[bucket_name] = bucket
            r['data']['Buckets'] = filtered
        if names_only is not None and names_only:
            buckets = r['data'].get('Buckets', {})
            names = [bucket_name for bucket_name, _ in buckets.items()]
            r['data']['Buckets'] = names

        return r

    def buckets_convert_to_archive(self, bucket_name: str):
        """Convert a backup to an archive
        """
        return Request(self, 'post', self._path('/buckets/archive/', bucket_name)).run().to_dict()

    def exports_list(self):
        """Retrieve all exports
        """
        return Request(self, 'get', self._path('/exports')).run().to_dict()

    def health(self):
        return Request(self, 'get', self._path('/health')).run().to_dict()

    def serial(self):
        return Request(self, 'get', self._path('/serial')).run().to_dict()

    def usage(self):
        return Request(self, 'get', self._path('/usage')).run().to_dict()

    def tasks_create(self, source: typing.Optional[str] = None,
                     destination: typing.Optional[str] = None,
                     copy_only: typing.Optional[bool] = None,
                     request: typing.Optional[dict] = None,
                     **kwargs):
        """Copy data from `source` to `destination`

        :param source: source URL . Example: nfs://nas.example.com/data
        :param source_path: The full path to copy from including the export (i.e., /data/dir1/dir2)
                            that must be rooted in the export directory
        :param destination: destination URL
        :param copy_only: only meaningful when copying data from a NAS to a backup location,
        in which case the CopyOnly parameter has the following effects on a copy from NAS to Igneous:
            False ‑ This mode behaves like an incremental backup. Files that were found by earlier
                    copy tasks but have since been deleted on the NAS source will be marked for
                    deletion on Igneous. The files marked for deletion will not be recovered by
                    the API copy task from Igneous to NAS. Your Igneous Customer Success team at
                    customersuccess@igneous.io can apply a retention policy to the bucket that will
                    periodically scan for files deleted beyond the retention period to remove from the system.
            True ‑ In contrast this mode never marks files for deletion on Igneous even if they’re
                   deleted from the source NAS. All files in the target Igneous bucket will
                   therefore be copied to the NAS target when using the API including files
                   that may have been deleted from the source NAS.
        """
        params = {}
        if copy_only is not None:
            params['CopyOnly'] = copy_only
        if request is None:
            request = {}
        if source is not None:
            request['source'] = source
        if destination is not None:
            request['destination'] = destination
        request['params'] = params
        payload = {**request, **kwargs}
        return Request(self, 'post', self._path('/tasks'), json=payload).run().to_dict()

    def tasks_list(self):
        """Retrieve current tasks
        """
        return Request(self, 'get', self._path('/tasks/')).run().to_dict()

    def tasks_get(self, task_id):
        """Retrieve the task with task ID `task_id`
        """
        return Request(self, 'get', self._path('/tasks/', task_id)).run().to_dict()

    def tasks_cancel(self, task_id):
        """Retrieve the task with task ID `task_id`
        """
        return Request(self, 'delete', self._path('/tasks/', task_id)).run().to_dict()

    def set_policy(self, policy_name, system_name, source_path):
        """Set policy on a backup
        """
        payload = {'Policy': policy_name, 'System': system_name, 'SourcePath': source_path}
        return Request(self, 'post', self._path('/policies/backup'), json=payload).run().to_dict()
