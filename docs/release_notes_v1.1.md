# Igneous API v1.1 Release Notes

Version 1.1 is fully backward compatible with V1.0. 

Documentation at http://kb.igneous.io./docs was updated to reflect v1.1 .

## 1. Python SDK

The Igneous API is now released with a Python SDK !

It can be found at :
- https://github.com/igneous-systems/python-igneous
<br/>and
- https://pypi.org/project/igneous

## 2. Copy API update

### 2.1 New data movement source & destination combinations

The endpoint to create a data movement task (POST /x/igneous/v1/tasks) is updated in v1.1 to accept a wider range of source and destination combinations.

Here are the valid combinations in version 1.0 of the API:

| **→ Destination type<br/>↓ Source type** | **native filer targets**:<br/>``nfs://HOST``<br/>``smb://HOST`` | **igneous target**<br/>``igneous://BUCKET`` | **compact cloud target**: <br/>``s3-compact://BUCKET`` |
| ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------------- | ------------------------------------------------------ |
| **``nfs://HOST``<br/>``smb://HOST``**    | ❌                                                            | ✅ Backup or Copy Task                       | ✅ Backup task                                          |
| **``igneous://BUCKET``**                 | ✅ Restore task                                               | ❌                                           | ❌                                                      |



And here are the valid combinations in version 1.1 of the API:

| **→ Destination<br/>type<br/>↓ Source type** | **native <br/>filer targets**:<br/>``nfs://HOST``<br/>``smb://HOST`` | **igneous target**:<br/>``igneous://bucket`` | **compact cloud targets**:<br/>``s3-compact://BUCKET``<br/>``azs-compact://BUCKET``<br/>``gcs-compact://BUCKET``<br/>``nfs-compact://BUCKET``<br/> | **native cloud targets:** <br/>``s3://BUCKET``<br/>``azs://BUCKET``<br/>``gcs://BUCKET`` |
| -------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| ``nfs://HOST``<br/>``smb://HOST``            | ✅ Copy Task                                                  | ✅ Backup or Copy Task                        | ✅ Backup or Copy task                                        | ✅ Copy task                                                  |
| ``igneous://BUCKET``                         | ✅ Restore task                                               | ❌                                            | ❌                                                            | ❌                                                            |
| ``s3://BUCKET``<br/>``azs://BUCKET``<br/>``gcs://BUCKET``| ✅ Copy Task   | ❌ | ❌ | ✅ Copy Task |


Note that while `nfs://HOST` is a native filer target and the URL host field needs to be the NFS host, but `nfs-compact://BUCKET` is a compact cloud target, and the URL host field needs to be the bucket name,

### 2.2 More flexibility in the syntax for data movement requests

In v1.0, the source and destination fields of a task request are strings, for instance:

```json
{
  "source": "nfs://HOST/EXPORT",
  "destination": "s3-compact://BUCKET/PATH?credential=USERNAME&tier=S3_TIER&region=S3_REGION&index=IGNEOUS_BUCKET"
}
```

V1.1 allows to _explode_ URL strings into JSON properties. For instance, the request above is equivalent to this one:

```json
{
  "source": {
    "url": "nfs://HOST/EXPORT"
  },
  "destination": {
    "url": "s3-compact://BUCKET/PATH",
    "credential": "USERNAME",
    "tier": "S3_TIER",
    "region": "S3_REGION",
    "index": "IGNEOUS_BUCKET"
  }
}
```

Any hybrid combination of parameters being specified as part of the URL string and as a JSON property is supported. For instance, this request is equivalent to the previous one:

```json
{
  "source": "nfs://HOST/EXPORT",
  "destination": {
    "url": "s3-compact://BUCKET/PATH?tier=S3_TIER&region=S3_REGION&index=IGNEOUS_BUCKET",
    "credential": "USERNAME"
  }
}
```

If a parameter is given in both the URL string and as a JSON parameter, the JSON parameter one overrides the one in the URL string, for instance, 

```json
{
  "url": "s3://BUCKET/PATH?tier=S3_TIER&index=IGNEOUS_BUCKET&region=S3_REGION",
  "region": "OTHER_REGION"
}
```

is effectively the same as this request:

```json
{
  "url": "s3://BUCKET/PATH?tier=S3_TIER&index=IGNEOUS_BUCKET&region=OTHER_REGION"
}
```



### 2.3 Transient credentials

v1.0 implements one auth scheme: stored credential: a username can be specified with the `credential=` query parameter , and that username is used to look up stored credentials at the Igneous system.

v1.1 implements 2 auth schemes:

- stored credential , just as v1.0 does;
- transient credentials: credentials for a cloud target can be given as part of the task request. They are used by the Igneous system for the given task, and then discarded. 

Transient credentials are specified with a set of `transient` parameters, which depend on the type of the target.

#### 2.3.1 AWS S3 Targets

Transient credentials are specified with the `accessKey` and `secretKey` parameters, either as query parameters or JSON properties.

Example:

```json
{
    "source": "nfs://nfshost/nfsexport",
    "destination": {
        "url": "s3://bucket1?region=us-west-2&tier=STANDARD&index=igbucket",
        "transient": {
          "accessKey": "AKIAQ4T2XKPLM26PC2U4",
          "secretKey": "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"
        }
    }
}
```

They can also be passed as URL query parameters; this request is equivalent to the previous one:
```json
{
    "source": "nfs://nfshost/nfsexport",
    "destination": "s3://bucket1?region=us-west-2&tier=STANDARD&index=igbucket&transient.accessKey=AKIAQ4T2XKPLM26PC2U4&transient.secretKey=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"
}
```

Note the special syntax with square brackets to specify transient credentials parameters as URL query parameters: `transient.accessKey` and `transient.secretKey`

#### 2.3.2 Azure Targets

Transient credentials are specified with the `accountName` and `accountKey` parameters, either as query parameters or JSON properties.

Example:

```json
{
  "source": "nfs://nfshost/nfsexport",
  "destination": {
    "url": "azs://bucket1?tier=Hot&index=igbucket",
    "transient": {
      "accountName": "user0",
      "accountKey": "password0"
    }
  }
}
```

They can also be passed as URL query parameters; this request is equivalent to the previous one:
```json
{
  "source": "nfs://nfshost/nfsexport",
  "destination": "azs://bucket1?tier=Hot&index=igbucket&transient.accountName=user0&transient.accountKey=password0"
}
```

#### 2.3.3 Google Cloud Targets

Transient credentials are specified with the `projectId` and `jwt` parameters, either as query parameters or JSON properties.

Example:

```json
{
  "source": "nfs://nfshost/nfsexport",
  "destination": {
    "url": "gcs://bucket1?tier=standard&index=igbucket",
    "transient": {
      "projectId": "project1",
      "jwt": "{\"Type\":\"service_account\",\"Project_id\":\"project1\",\"Private_key_id\":\"324a56f75017adfd7bab089e157f29626d32e735\",\"Private_key\":\"-----BEGIN+PRIVATE+KEY-----\nMIIEvgIBADANBgkqhkiG9e0BAQEFAASCBKgwggSkAgEAAoIBAQCYqzsYhSwwpG92\nSin8+RSaAMgX7WoyqP/znL1x7jMcPJzSAS/WNxu4VNbs/fPW9UVI9FFP38vi3MV7\n656w94LuCBLIC6xA4JkTDkb6Zh0OtD+cpHUp71SsjBOH7ud/aRXHZ3V6kNvWJjO/\nPmSEyj37DHQ63vJ1J2MB79QRZg/PMQwBR91nwjlqO0rzEuq9zRdBnDmzjmSrH3/h\nttOiM/zSTPj9cd5ut01fIcuiuhVzHuKaH6kT/GhgTz2so5pVb6uB6pQJFxuWLcJJ\nqorEYhIfMmv3cbpjRhbeflP2AGg4+Bf1pFMbzROhSupiA1g/sQH9VF87LjSEmY+R\n/mgUkgX3AgMBAAECggEAEW6DueIC0K8F1xDSyIK8OnVaY3kFRjGLwAomi2qyRUga\nc9QU3TW/oYV2YOsCO4oX1iOnYSJhik7A8cxQTv6D4Z/kXRkQGvxKHiXkLtUX/kTQ\nepdAlYAxP95ioIPDxQV/qhwDCvKdV09XWz/JhGv/NboPT2WDc6MCqAb1RONNbM+0\ns1Ed0Xj0M0Hqf+XO7rRiMRBfmykzzTMS1ZRiCMhQikoVZu9i58uykc1CYJxHmwJs\nCoWgaRgi2Rva8jFW4Zzcnw+zt8zx6gsLKOSAfkEmfLfQgGDWr0p7UNDaIl6DvSzF\ndd7EA4AsPlE+aj5dJfngQbQNyy6DC29sN8M/eHTemQKBgQDI3no7xiTj37h29uH9\nt+qGaCJH2jyMJhZ9AsM2ZJO2KCw4SICCZhBMMSsIc5QeBRP9Y0kapvVYHk1IW74e\nI/Gjoued2Fj5Tz9DkK1p0m4S4RB2wnRFLa7c2eP+rsFBwWv/OWIoluyjyK1GNfTD\n/R3dMQMgKkeEt5wiweUMC3h6dQKBgQDCkhj1h8sNEz95o/wk8LKbEDHFZARkxUDX\nmyNixMgEne1yboKFj0BkyNeom1W3r2JnskhGjvIyZFTQrKyoiEKHr4QL/+9xB+qo\nDTF+CpAcMIplaX38aAMJ34M1UVnUv3DpVNTMQkvD4rD6xwFtwt1fljgnHD+pVjGb\nxzA0U6r5OwKBgQCn2mnQe2KmXXQ7TVFKAJ9lU62Z13+TKdzO+DkCwgdBR86z9boV\nvY5O7SNlu5eBgoLS0l3rfKs2yJOSLL/xVd39/QqJt5maNCPMpSCUdnjvI83rP9GD\nYYpnGVlRoNzzwtspet1Qx9XVg8NwEXSJNoH3LZbMESiUeg5qaRaq+wbhZQKBgQCB\ntbfh51ccLlrAkuvDDJtk+FTVzKmJLF7f3VKnw5u8SDRFdxqYQzmgdqwegP+R5t/p\nVVcNgro/kddhDdxEtiH0JrQW89YCOk7bHYCDEDOmN03r8XnFzOlJqbHk14jVZZK2\nWpFKYl/0BKoLZKO1MpU15gUlPZXLI+UKfq3KFIUEhQKBgC9u+9xEnNEFJqO2ugtz\nyeWszgXBbwsHkULITpjPMqZScrlEZb6xI6cVvpyDwlnMuuhn/f73gMlMJoaO1EVX\nWJxXzeNwNgZPxsu84zpL3+tIXMcp7kkjQw5xrCqB6NfUGa2qinZMQu0ipBbYmueG\n5fGfiJzpA7QvJX4xlZX2sq/n\n-----END+PRIVATE+KEY-----\n\",\"Client_email\":\"igneous-tier1@project1.iam.gserviceaccount.com\",\"Client_id\":\"109940094586184102946\",\"Auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"Token_uri\":\"https://oauth2.googleapis.com/token\",\"Auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"Client_x509_cert_url\":\"https://www.googleapis.com/robot/v1/metadata/x509/igneous-tiering%40tiering-170717.iam.gserviceaccount.com\"}"
    }
  }
}
```

They can also be passed as URL query parameters; this request is equivalent to the previous one:
```json
{
  "source": "nfs://nfshost/nfsexport",
  "destination": "gcs://bucket1?tier=standard&index=igbucket&transient.projectId=project1&transient.jwt=%7B%22Type%22%3A%22service_account%22%2C%22Project_id%22%3A%22project1%22%2C%22Private_key_id%22%3A%22324a56f75017adfd7bab089e157f29626d32e735%22%2C%22Private_key%22%3A%22-----BEGIN+PRIVATE+KEY-----%5CnMIIEvgIBADANBgkqhkiG9e0BAQEFAASCBKgwggSkAgEAAoIBAQCYqzsYhSwwpG92%5CnSin8%2BRSaAMgX7WoyqP%2FznL1x7jMcPJzSAS%2FWNxu4VNbs%2FfPW9UVI9FFP38vi3MV7%5Cn656w94LuCBLIC6xA4JkTDkb6Zh0OtD%2BcpHUp71SsjBOH7ud%2FaRXHZ3V6kNvWJjO%2F%5CnPmSEyj37DHQ63vJ1J2MB79QRZg%2FPMQwBR91nwjlqO0rzEuq9zRdBnDmzjmSrH3%2Fh%5CnttOiM%2FzSTPj9cd5ut01fIcuiuhVzHuKaH6kT%2FGhgTz2so5pVb6uB6pQJFxuWLcJJ%5CnqorEYhIfMmv3cbpjRhbeflP2AGg4%2BBf1pFMbzROhSupiA1g%2FsQH9VF87LjSEmY%2BR%5Cn%2FmgUkgX3AgMBAAECggEAEW6DueIC0K8F1xDSyIK8OnVaY3kFRjGLwAomi2qyRUga%5Cnc9QU3TW%2FoYV2YOsCO4oX1iOnYSJhik7A8cxQTv6D4Z%2FkXRkQGvxKHiXkLtUX%2FkTQ%5CnepdAlYAxP95ioIPDxQV%2FqhwDCvKdV09XWz%2FJhGv%2FNboPT2WDc6MCqAb1RONNbM%2B0%5Cns1Ed0Xj0M0Hqf%2BXO7rRiMRBfmykzzTMS1ZRiCMhQikoVZu9i58uykc1CYJxHmwJs%5CnCoWgaRgi2Rva8jFW4Zzcnw%2Bzt8zx6gsLKOSAfkEmfLfQgGDWr0p7UNDaIl6DvSzF%5Cndd7EA4AsPlE%2Baj5dJfngQbQNyy6DC29sN8M%2FeHTemQKBgQDI3no7xiTj37h29uH9%5Cnt%2BqGaCJH2jyMJhZ9AsM2ZJO2KCw4SICCZhBMMSsIc5QeBRP9Y0kapvVYHk1IW74e%5CnI%2FGjoued2Fj5Tz9DkK1p0m4S4RB2wnRFLa7c2eP%2BrsFBwWv%2FOWIoluyjyK1GNfTD%5Cn%2FR3dMQMgKkeEt5wiweUMC3h6dQKBgQDCkhj1h8sNEz95o%2Fwk8LKbEDHFZARkxUDX%5CnmyNixMgEne1yboKFj0BkyNeom1W3r2JnskhGjvIyZFTQrKyoiEKHr4QL%2F%2B9xB%2Bqo%5CnDTF%2BCpAcMIplaX38aAMJ34M1UVnUv3DpVNTMQkvD4rD6xwFtwt1fljgnHD%2BpVjGb%5CnxzA0U6r5OwKBgQCn2mnQe2KmXXQ7TVFKAJ9lU62Z13%2BTKdzO%2BDkCwgdBR86z9boV%5CnvY5O7SNlu5eBgoLS0l3rfKs2yJOSLL%2FxVd39%2FQqJt5maNCPMpSCUdnjvI83rP9GD%5CnYYpnGVlRoNzzwtspet1Qx9XVg8NwEXSJNoH3LZbMESiUeg5qaRaq%2BwbhZQKBgQCB%5Cntbfh51ccLlrAkuvDDJtk%2BFTVzKmJLF7f3VKnw5u8SDRFdxqYQzmgdqwegP%2BR5t%2Fp%5CnVVcNgro%2FkddhDdxEtiH0JrQW89YCOk7bHYCDEDOmN03r8XnFzOlJqbHk14jVZZK2%5CnWpFKYl%2F0BKoLZKO1MpU15gUlPZXLI%2BUKfq3KFIUEhQKBgC9u%2B9xEnNEFJqO2ugtz%5CnyeWszgXBbwsHkULITpjPMqZScrlEZb6xI6cVvpyDwlnMuuhn%2Ff73gMlMJoaO1EVX%5CnWJxXzeNwNgZPxsu84zpL3%2BtIXMcp7kkjQw5xrCqB6NfUGa2qinZMQu0ipBbYmueG%5Cn5fGfiJzpA7QvJX4xlZX2sq%2Fn%5Cn-----END+PRIVATE+KEY-----%5Cn%22%2C%22Client_email%22%3A%22igneous-tier1%40project1.iam.gserviceaccount.com%22%2C%22Client_id%22%3A%22109940094586184102946%22%2C%22Auth_uri%22%3A%22https%3A%2F%2Faccounts.google.com%2Fo%2Foauth2%2Fauth%22%2C%22Token_uri%22%3A%22https%3A%2F%2Foauth2.googleapis.com%2Ftoken%22%2C%22Auth_provider_x509_cert_url%22%3A%22https%3A%2F%2Fwww.googleapis.com%2Foauth2%2Fv1%2Fcerts%22%2C%22Client_x509_cert_url%22%3A%22https%3A%2F%2Fwww.googleapis.com%2Frobot%2Fv1%2Fmetadata%2Fx509%2Figneous-tiering%2540tiering-170717.iam.gserviceaccount.com%22%7D"
}
```

NB: the Google Cloud JWT key needs to be URL encoded if passed as a URL query parameter (we recommend passing it as a JSON property, which has a syntax less prone to entry errors)

### 2.4 Independent prefix paths on source & destination

In V1.0 a top-level `path` JSON property specifies a prefix path for both source and destination filer locations.

In V1.1, prefix paths are specified independently on the source and destination locations with the `prefix` parameter.

Example:

```json
{
  "source": "nfs://host1/export1?prefix=export1/path1",
  "destination": "nfs://host2/export2?prefix=export2/path2"
}
```



## 3. New API: Cloud-Bucket Usage API
New API to report the amount of physical data in a cloud bucket for a given export path of a system.

### 3.1 Cloud-Bucket Usage API Syntax
 Prerequisites:
 1. Exports should be attached with policies that take back to the cloud buckets(which are set up with credentials in the Igneous system).

 API Syntax: 
```$xslt
Method:
      HTTP GET
End point:
      /x/igneous/v1/cloud-buckets/usage
Input parameters:
      1. systemName
          Description: "Name of the system"
          Required: yes
          Type: string
      2. exportPath
          Description: "Path of the export"
          Required: yes
          Type: string
Output:
      1. Success(HTTP/1.1 200 OK) response:
        {
          1. Source Size
                Description: "Latest count of the size in GiB on the primary filer"
                Type: int64
          2. Remote Size
                Description: "Size in GiB of data on cloud sources"
                Type: array of RemoteSize
                      RemoteSize structure:
                        {
                            Location:
                                Description: "Cloud provider (azs/aws/gcs)"
                                Type: string
                            CloudBucket:
                                Description: "Name of the cloud bucket where the backup resides"
                                Type: string
                            Usage:
                                Description: "Usage size in GiB"
                                Type: int64
                            Host:
                                Description: "Host information (Applicable for custom s3)"
                                Type: string
                            Account:
                                Description: "Account name"
                                Type: string
                        }
        }

      2. Failure(HTTP/1.1 401 Unauthorized) response:
         When API is accessed without creating the token and authorization.

      3. Failure(HTTP/1.1 404 Not Found) response:
            a. {} Empty response is returned when an invalid exportPath is specified.
            b. {"Error":"GetSystemByName: name "<>" not found"} 
                  Error response is returned when invalid value for systemName is provided.
```
NOTE: Source Size and Remote Size Usage is always represented in GiB (not GB) and is rounded off. i.e. if 
      Source Size is 0.6GiB, it would be shown as 1GiB and if Source Size is 0.4GiB it would be shown as 0GiB. 
### 3.2 API usage example:
```go
iggy customerapi -s local createapitoken

export AUTH="Authorization: GEIVH2TSRJEQ6MUP0QN7"

curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvol.iggy.bz&exportPath=/smallvol/jahnavi1' | jq .
```

#### 3.2.1 Success scenario examples:
1. Cloud bucket usage when valid system name and export path(with small amount of data) are provided. 
Note: /smallvol/jahnavi1 has data size as 4.1KB 
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvol.iggy.bz&exportPath=/smallvol/jahnavi1' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   252  100   252    0     0  10276      0 --:--:-- --:--:-- --:--:-- 10500
{
  "SourceSize": 0,
  "RemoteSize": [
    {
      "Location": "s3",
      "CloudBucket": "jahnavitest",
      "Usage": 0
    },
    {
      "Location": "gcs",
      "CloudBucket": "jahnavitest",
      "Usage": 0,
      "Account": "tiering-170717"
    },
    {
      "Location": "azs",
      "CloudBucket": "jahnavitest",
      "Usage": 0,
      "Account": "cswtesting"
    }
  ]
}

```
2. Cloud bucket usage when valid system name and export path(having considerable amount of data) are provided.
Note: /chip1253/chip1253qa has data size of 778.1MB
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=netapp42-admin.iggy.bz&exportPath=/chip1253/chip1253qa' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   112  100   112    0     0  12585      0 --:--:-- --:--:-- --:--:-- 14000
{
  "SourceSize": 1,
  "RemoteSize": [
    {
      "Location": "azs",
      "CloudBucket": "jahnavitest",
      "Usage": 1,
      "Account": "cswtesting"
    }
  ]
}

```

3. When valid system name and export path are specified (but, the exportPath has no policy attached to it)
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvol.iggy.bz&exportPath=/smallvol/jahnavi2' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    35  100    35    0     0   6468      0 --:--:-- --:--:-- --:--:--  7000
{
  "SourceSize": 0,
  "RemoteSize": null
}
```

#### 3.2.2 Failure scenario examples:

1.  When API is accessed without creating the token and authorization
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvl.iggy.bz&exportPath=/smallvol/jahnavi3' -i
HTTP/1.1 401 Unauthorized
Date: Tue, 15 Sep 2020 22:41:33 GMT
Content-Length: 0
```

```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvl.iggy.bz&exportPath=/smallvol/jahnavi3' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
```
2. Invalid systemName is specified
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvl.iggy.bz&exportPath=/smallvol/jahnavi3' -i
HTTP/1.1 404 Not Found
Content-Length: 60
Content-Type: text/plain; charset=utf-8
Date: Tue, 15 Sep 2020 22:40:06 GMT
X-Request-Id: 78b795a7-f401-4a39-87ff-d0e3114636d4

{"Error":"GetSystemByName: name smallvl.iggy.bz not found"}
```
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvl.iggy.bz&exportPath=/smallvol/jahnavi3' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    60  100    60    0     0  14513      0 --:--:-- --:--:-- --:--:-- 20000
{
  "Error": "GetSystemByName: name smallvl.iggy.bz not found"
}
```
3. Invalid exportPath is specified
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvol.iggy.bz&exportPath=/smallvol/jahnavi3' -i
HTTP/1.1 404 Not Found
Content-Length: 3
Content-Type: text/plain; charset=utf-8
Date: Tue, 15 Sep 2020 22:39:23 GMT
X-Request-Id: c438c021-d00a-4894-a666-f4d852484d78

{}
```
```go
ubuntu@ip-172-31-52-122:~/mesa$ curl -H "$AUTH" -X GET 'http://172.19.0.4/x/igneous/v1/cloud-buckets/usage?systemName=smallvol.iggy.bz&exportPath=/smallvol/jahnavi3' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100     3  100     3    0     0    811      0 --:--:-- --:--:-- --:--:--  1000
{}
```
