#!/bin/bash

set -euo pipefail
# set -x

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}== flake8 ==${NC}"
flake8 machine_plugins/
flake8 setup.py
echo -e "${GREEN}== flake8 done ==${NC}"
echo -e "${GREEN}== brunette ==${NC}"
# --diff because black/brunette
brunette --diff --check machine_plugins/ --config=setup.cfg
brunette --diff --check tests/ --config=setup.cfg
brunette --diff --check setup.py --config=setup.cfg
echo -e "${GREEN}== brunette done ==${NC}"
echo -e "${GREEN}== pytest ==${NC}"
pytest -v --cov=machine_plugins --cov-report=html tests/
echo -e "${GREEN}== pytest done==${NC}"
