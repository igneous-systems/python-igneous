# Curl wrapper functions

From a bash shell, start by sourcing the `curl_wrappers.sh` :

```bash
. ./curl_wrappers.sh
```

That will put 2 functions. in your bash session: `igget` and `igpost` (you can see what they do with `declare -f <function_name>`)


# igget

`igget` sends a GET request to the Igneous API. 

`igget ENDPOINT [CURL_ARGS]`

`ENDPOINT` is the endpoint to hit on the API (e.g. `tasks`), `CURL_ARGS` is an optional list of arguments to pass to curl.

Example: retrieve current tasks:

```bash
> igget tasks
{"Tasks":[],"Total":0}
```

`igget` is a very light wrapper around curl; you can append regular curl options, for instance:

```bash
> igget tasks --include
HTTP/1.1 200 OK
Content-Length: 23
Content-Type: application/json
Date: Fri, 28 Aug 2020 07:13:06 GMT
X-Request-Id: 7ca8ed8f-0dd2-4ad5-8a50-4fd99888335f
X-Request-Id: 60ec0695-2610-4617-a463-4abd24cf2de9

{"Tasks":[],"Total":0}
```

To retrieve buckets on the system you would say:

```bash
> igget buckets
[... very long JSON output ...]
```

You can use `jq` to help with reading the output. For instance, for `buckets`, the top element is `Buckets` :

```bash
> igget buckets | jq .Buckets
```

You'll find the full API v1.0 documentation [here](https://kb.igneous.io/docs/en/get-bucket-information) .

# igpost

`igpost` sends a POST request to the Igneous API.

`igpost ENDPOINT PAYLOAD_FILE [CURL_ARGS]`

- `ENDPOINT` is the endpoint to hit on the API (e.g. `tasks`),
- `PAYLOAD_FILE` is the JSON file that contains the POST payload for the request. Note that `igpost` does not support passing the JSON payload inline with the command.
- `CURL_ARGS` is an optional list of arguments to pass to curl.

You will find example JSON payload files under `curl/examples/data-copy`
Each JSON file in `curl/examples/data-copy` represents a specific data movement request. 

For example, here's the content of `nfs-to-s3-native-copy.json` :

```json
{
  "source": "nfs://NFS_HOST/NFS_EXPORT_PATH",
  "destination": {
    "url": "s3://BUCKET",
    "region": "us-west-2",
    "tier": "STANDARD",
    "credential": "STORED_CREDENTIAL",
    "index": "INDEX"
  }
}
```

To run it:

```bash
> igpost tasks nfs-to-s3-native-copy.json
```

To which you will get a response similar to this:

```json
{
  "Tasks": [
    { 
      "ID": "YTU4Y2JiMWUzZTM0MWFhODU1Mjg3Yzg0YzY4MGYzZDI=",
      "State": "pending"
   }
  ],
  "Total":0
}
```

Note how the response contains the ID for the created task. 
You can poll its status with `igget tasks/{taskId}` , in this case:

```bash
> igget tasks/YTU4Y2JiMWUzZTM0MWFhODU1Mjg3Yzg0YzY4MGYzZDI= | jq
{
  "Tasks": [
    {
      "ID": "YTU4Y2JiMWUzZTM0MWFhODU1Mjg3Yzg0YzY4MGYzZDI=",
      "State": "finished",
      "Started": "2020-08-28T14:24:54.743544Z",
      "Finished": "2020-08-28T14:25:04.736429Z",
      "Summary": {
        "Files": {
          "Processed": 3,
          "Skipped": 0
        },
        "Links": {
          "Processed": 0,
          "Skipped": 0
        },
        "Dirs": {
          "Processed": 3,
          "Skipped": 0
        },
        "BytesProcessed": 7223901,
        "BytesSkipped": 0,
        "Errors": 0
      }
    }
  ],
  "Total": 1
}
```


## Writing JSON payload files

The API supports 2 syntaxes for the `"source"` and `"destination"` fields : 
URL strings (like in v1.0) or JSON objects. 
If using JSON objects, you can _explode_ the url query parameters as JSON properties. For instance:

```json
{
  "source": "nfs://host/path?prefixPath=path/subpath",
  "destination": "igneous:///bucket"
}
```

is equivalent to:

```json
{
  "source": {
    "url": "nfs://host/path",
    "prefixPath": "path/subpath"
  },
  "destination": {
    "url": "igneous:///bucket"
  }
}
```






