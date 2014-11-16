develop:
	pip install -e .
	make install-test-requirements

install-test-requirements:
	pip install "file://`pwd`#egg=urllib3-mock[tests]"

test: develop lint
	@echo "Running Python tests"
	py.test .
	@echo ""

lint:
	@echo "Linting Python files"
	flake8 .
	@echo ""
