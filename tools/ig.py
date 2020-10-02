#!/usr/bin/env python3

import click
from dotenv import load_dotenv
import sys
import json

try:
    import igneous
except ModuleNotFoundError:
    # Try to see if we are in a dev layout:
    sys.path.append("..")
    import igneous


def empty(x):
    return x is None or len(x) == 0


PRINT_REQUEST = False


def json_dumps(d):
    return igneous.json_dumps(d).replace('\n', '\n  ')


def print_response(r):
    keys = 'request,reason,code,data,ok' if PRINT_REQUEST else 'reason,code,data,ok'
    click.echo('{ ' + ',\n  '.join([f'"{k}": ' + json_dumps(r[k]) for k in keys.split(',') if k in r]) + ' }')


client = igneous.Client()


@click.group()
@click.option('--api-key', '-k', required=True, envvar="IGNEOUS_API_KEY", help="Igneous API key")
@click.option('--api-server', '-s', required=True, envvar="IGNEOUS_API_SERVER", help="Igneous API server")
@click.option('--dry-run', is_flag=True, help="Print out request that would be sent to API but don't run it")
@click.option('-r', '--print-request', is_flag=True, help="Print the request as part of the response")
@click.option('-a', '--api-version', help="Defaults to v1. Can be: v1, v1.0 or v1.1")
def cli(api_key, api_server, dry_run, print_request, api_version):
    """Igneous API command line tool

    The API server and key are required, and can be provided in 3 different ways:

\b
    - as command line options; example:
        ig.py -k WMMKOAO2BWXDHJXTSUHT -s 10.105.0.22
    - via the IGNEOUS_API_KEY AND IGNEOUS_API_SERVER
      environment variables; example:
        export IGNEOUS_API_KEY=WMMKOAO2BWXDHJXTSUHT
        export IGNEOUS_API_SERVER=10.105.0.22
        ./ig.py
    - via a .env file; example:
        cat>.env
            IGNEOUS_API_KEY=WMMKOAO2BWXDHJXTSUHT
            IGNEOUS_API_SERVER=10.105.0.22
        ./ig.py
    - you may have several env files, and switch between them from the shell:
        ln -s sim.env .env
        ./ig.py
    """
    global client, PRINT_REQUEST
    client = igneous.Client(api_server=api_server, api_key=api_key, dry_run=dry_run, api_version=api_version)
    PRINT_REQUEST = print_request or dry_run


@cli.command()
def version():
    """Report the API server version
    """
    r = client.get_version()
    print_response(r)


@cli.group()
def buckets():
    """list buckets
    """


@buckets.command('list')
@click.option('-s', '--system', help="Only list information for buckets protecting exports on the specified system")
@click.option('-m', '--match', help="Match bucket name")
@click.option('-n', '--names-only', is_flag=True, help="Return bucket names only (and not their info)")
def buckets_list(system, match, names_only):
    """List bucket information
    """
    r = client.buckets_list(system_name=system, match=match, names_only=names_only)
    print_response(r)


@buckets.command('systems')
@click.option('-s', '--system', help="Only list information for buckets protecting exports on the specified system")
def buckets_systems(system):
    """List systems used across all buckets
    """
    r = client.buckets_get(system_name=system)
    systems = {}
    for bucket_name, bucket in r.get('data', {}).get('Buckets', {}).items():
        s = bucket.get('System', '')
        path = bucket.get('SourcePath', '')
        if s not in systems:
            systems[s] = set()
        systems[s].add(path)
    r['data'] = {k: sorted(list(v)) for k, v in systems.items()}
    print_response(r)


@buckets.command('get')
@click.argument('bucket_name')
def buckets_get(bucket_name):
    """Retrieve one bucket by name
    """
    r = client.buckets_get(bucket_name=bucket_name)
    print_response(r)


@cli.group()
def policies():
    """Manage policies on exports
    """
    pass


@policies.command('set')
@click.option("-p", "--policy", required=True, help="Policy name to apply to the given export")
@click.option("-s", "--system", required=True, help="System name export path belongs to")
@click.option("-x", "--export", required=True, help="Export path to apply policy to, e.g. /ifs/home")
def policies_set(policy, export, system):
    """Set a policy on a specified export
    """
    r = client.set_policy(policy, system, export)
    print_response(r)


@policies.command('clear')
@click.option("-s", "--system", required=True, help="System name export path belongs to")
@click.option("-x", "--export", required=True, help="Export path to apply policy to, e.g. /ifs/home")
def policies_clear(system, export):
    """Clear a policy on a specified export
    """
    # Setting a policy with empty string clears the policy association
    r = client.set_policy("", system, export)
    print_response(r)


@cli.group()
def tasks():
    """Get task info by ID, list currently running tasks, and create new, on-demand tasks
    """
    pass


@tasks.command('list')
def tasks_list():
    """List all running and queued tasks
    """
    r = client.tasks_list()
    print_response(r)


@tasks.command('get')
@click.argument("task_id")
def tasks_get(task_id):
    """Get information for a specific task by ID
    """
    r = client.tasks_get(task_id)
    print_response(r)


@tasks.command('cancel')
@click.argument("task_id")
def tasks_cancel(task_id):
    """Delete a task
    """
    r = client.tasks_cancel(task_id)
    print_response(r)


"""
./igneous tasks create source.url="nfs://export" source.prefixPath="rw"
"""


@tasks.command('create')
@click.option('-s', '--source')
@click.option('-d', '--destination')  # , nargs=-1)
@click.option('-f', '--file', type=click.File('r'), multiple=True,
              help="Read the task creation parameters from a file on the local system")
@click.option('-p', '--path', help="The full path to copy from including the export mount"
                                   " path (i.e., /data/dir1/dir2) that must be rooted in"
                                   " the export directory")
@click.option('-c', '--copy-only', help="When set, task won't mark files for deletion on "
                                        "Igneous even if they’re deleted from the source NAS",
              default=False, is_flag=True)
@click.option('-x', '--extra', multiple=True)
def tasks_create(source, destination, file, path, copy_only, extra):
    """Create on-demand tasks to run on the Igneous system.

    SOURCE: URL specification for either an Igneous bucket or an NFS/SMB dataset.

    DESTINATION: URL specification for either an Igneous bucket or an NFS/SMB dataset.
    """
    payload = {}
    for f in file:
        payload = {**payload, **json.load(f)}
    extras = {} if extra is None else {k: v for k, v in [x.split('=', 1) for x in extra]}
    print(source, destination, payload, extras)
    if source is not None:
        payload['source'] = source
    if destination is not None:
        payload['destination'] = destination

    r = client.tasks_create(source, destination, copy_only, payload, **extras)
    # r = client.tasks_create(source, path, destination, copy_only,
    #                         **(
    print_response(r)


@cli.group()
def exports():
    """Info about exports
    """
    pass


@exports.command('list')
def exports_list():
    """List exports on the system
    """
    r = client.exports_list()
    print_response(r)


@cli.command()
@click.argument("path")
def get(path):
    """Run a generic GET command on the API
    """
    r = client.get(path)
    print_response(r)


@cli.command()
def health():
    """Show system health
    """
    r = client.health()
    print_response(r)


@cli.command()
def serial():
    """Show system serial
    """
    r = client.serial()
    print_response(r)


@cli.command()
def usage():
    """Show system usage
    """
    r = client.usage()
    print_response(r)


if __name__ == "__main__":
    load_dotenv(verbose=True)
    cli()
