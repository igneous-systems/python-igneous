"""
A simple example using the Python SDK to restore data from the Igneous System onto an NFS export.

This example program assumes that IGNEOUS_API_SERVER and IGNEOUS_API_KEY are set in the environment.

This example program takes 3 command-line arguments:
 - the name of the bucket at the Igneous system to restore from
 - the destination NFS host
 - the destination NFS path to restore to

"""
import os
import sys
import time

import igneous

if len(sys.argv) != 4:
    print("USAGE: ", sys.argv[0], " <Igneous Bucket name> <NFS host> <NFS path>")
    sys.exit(1)

igneous_bucket_name, nfs_host, nfs_path = sys.argv[1:]

# Create the Source URL:
source = 'igneous:///' + igneous_bucket_name

# Create the Destination URL:
destination = 'nfs://' + nfs_host + '/' + nfs_path

client = igneous.Client(api_server=os.environ['IGNEOUS_API_SERVER'], api_key=os.environ['IGNEOUS_API_KEY'])
print(source, '-->', destination)
response: dict = client.tasks_create(source=source, destination=destination)

"""
A successful response will always have this structure:

{
    "ok": true,
    "reason": "OK",
    "code": 200,
    "request": {
        "url": "<SERVER URL THAT WAS ACTUALLY HIT>"
        "method": "post",
        "headers": {
            "Authorization": "<THE CONTENT OF IGNEOUS_API_KEY>",
            "Content-Type": "application/json"
        },
        "payload": {
            "destination": "<DESTINATION URL>",
            "params": {},
            "source": "<SOURCE URL>"
        },
    }
    "data": {
        "Tasks": [
            {
                "ID": "<TASK ID OF THE TASK THAT WAS JUST CREATED>",
                "State": "pending",
                "TargetBucket": "<DESTINATION BUCKET>"
            }
        ],
        "Total": 0
    },
}
           
"""

if not response['ok']:
    print(igneous.pretty_format(response))
    sys.exit(2)

task = response['data']['Tasks'][0]

# This is the task ID of the task that was just created:
task_id = task['ID']  # It is an opaque string uniquely identifying the task

# This is the current state of that task at the Igneous system.
task_state = task['State']  # It can be one of: 'pending', 'running', 'finished' or 'failed'
print(task_state)

# Task was sent. Now poll repeatedly for the task status until it's done:
while task_state == 'pending' or task_state == 'running':
    time.sleep(3)  # Sleep 3 seconds
    response: dict = client.tasks_get(task_id)
    if not response['ok']:
        break

    """Example of successful response we get here:
    {
        "ok": true,
        "reason": "OK",
        "code": 200,
        "data": {
            "Tasks": [
                {
                    "Finished": "2020-10-07T19:42:55.99944Z",
                    "ID": "TASKID1",
                    "Started": "2020-10-07T19:42:36.573733Z",
                    "State": "finished",
                    "Summary": {
                      "BytesProcessed": 10571162,
                      "BytesSkipped": 0,
                      "Dirs": {
                          "Processed": 3,
                          "Skipped": 0
                      },
                      "Errors": 0,
                      "Files": {
                          "Processed": 4,
                          "Skipped": 0
                      },
                      "Links": {
                          "Processed": 0,
                          "Skipped": 0
                      }
                    },
                    "TargetBucket": "bucket1"
                }
            ],
            "Total": 1
        },
    }
    """

    task = response['data']['Tasks'][0]
    task_state = task['State']
    print(task_state)

# Done polling for task state.
# Whether successful or not, print the response:
print(igneous.pretty_format(response))

"""Example of successful response when task is finished:
{
    "code": 200,
    "data": {
        "Tasks": [
            {
                "Finished": "2020-10-07T20:11:15.999538323Z",
                "ID": "TASKID2",
                "Started": "2020-10-07T20:10:56.053056297Z",
                "State": "finished",
                "Summary": {
                    "BytesProcessed": 10583450,
                    "BytesSkipped": 10583450,
                    "Dirs": {
                        "Processed": 0,
                        "Skipped": 3
                    },
                    "Errors": 0,
                    "Files": {
                        "Processed": 0,
                        "Skipped": 4
                    },
                    "Links": {
                        "Processed": 0,
                        "Skipped": 0
                    }
                },
                "TargetBucket": "guirava1"
            }
        ],
        "Total": 1
    },
    "ok": true,
    "reason": "OK",
    "request": {
        "headers": {
            "Authorization": "<API_KEY>"
        },
        "method": "get",
        "payload": null,
        "url": "http://10.105.0.22/x/igneous/v1/tasks/TASKID2"
    }
}
"""
