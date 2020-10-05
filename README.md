# python-igneous
Igneous API Client SDK version 1.1.1

This is the Python client library for Igneous' APIs.

Available at: 

- https://github.com/igneous-systems/python-igneous
and
- https://pypi.org/project/igneous

Please refer to the Igneous API documentation at https://kb.igneous.io/docs for an introduction ;

For an example on how to use this SDK, see `tools/ig.py` , a command line tool for interacting with Igneous' APIs,
written with this very `igneous` package

## About versioning

The Igneous API is versioned with 1 major number and 1 minor number; the current version is 1.1 .

The Python SDK is version with 3 numbers: the first 2 are that of the Igneous API it is built for, and the third 
one reflects changes only on the client SDK side. The current version is 1.1.1.

## Resources you will find in this repo

- obviously the most notable one is the Python SDK under `igneous/`. The SDK under `igneous/` is also available as
  a Python package from PyPi : https://pypi.org/project/igneous
- `docs/` contains documentation about the Igneous API, in particular release notes with each new version of the API
- `curl/` contains wrappers and example for reaching the Igneous API with `curl`