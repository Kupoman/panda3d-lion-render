## Setup development environment
```bash
virtualenv venv
. venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

## Run Lint
Linting is done with pylint, and can be run with the Makefile.
```bash
make lint
```

## Run Tests
Unit testing is done with pytest, and can be run with the Makefile.
```bash
make test
```
