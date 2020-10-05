.PHONY: clean pypi

clean:
	rm -rf build dist *.egg-info

dist:
	python3 setup.py sdist bdist_wheel

# Update pypi (from https://packaging.python.org/tutorials/packaging-project)
#
# This assumes these packages are installed: setuptools wheel twine
# ~/.pypirc needs to list a valid pypi token. Example:
# > cat ~/.pypirc
# [pypi]
#  username = __token__
#  password = pypi-AgEIcHlwI3MjUyNQACJXsicGVybWlzc2lvbnMiOiA7dXNlciIsICJ2ZXJzaW9uIjogMX0AAAYgMLKU
pypi: dist
	python3 -m twine upload dist/*