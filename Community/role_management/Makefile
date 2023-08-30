PYTHON := python3.9
PYBINDPLUGIN := `$(PWD)/venv/bin/python -c 'import os;`

install-env:
	pip install -r requirements.txt


setup-unittest:
	virtualenv -p $(PYTHON) venv_test
	$(PWD)/venv_unittest/bin/pip install -r test/unittest/requirements.txt
unittest:
	@echo "Run test and export report test case"
	$(PWD)/venv_unittest/bin/coverage run --rcfile=test/unittest/.coveragerc  -m unittest discover -t ../../.. -s test/unittest/
	$(PWD)/venv_unittest/bin/coverage report
	$(PWD)/venv_unittest/bin/coverage html -d coverage_html
