VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python
FASTAPI_PORT := 8000
DEBUG_PORT := 5678
BACKEND_DIR := back

VUE_PORT := 5173
FRONTEND_DIR := front

install:
	@cd $(BACKEND_DIR) && export UV_PYTHON=$(PYTHON) && uv venv $(VENV_NAME) --clear && \
	. $(VENV_NAME)/bin/activate && \
	uv pip compile requirements.in -o requirements.txt && \
	uv pip install -r requirements.txt -r requirements-dev.txt && \
	pre-commit install && \
	cd ../$(FRONTEND_DIR) && \
	npm install

kill:
	@echo "Freeing required ports: $(FASTAPI_PORT) $(VUE_PORT) $(DEBUG_PORT)...\n"; \
	pids=$$(lsof -t -i:$(FASTAPI_PORT) -i:$(DEBUG_PORT) -i:$(VUE_PORT) 2>/dev/null); \
	if [ -n "$$pids" ]; then \
	  echo "Killing processes: $$pids"; \
	  kill -9 $$pids; \
	fi

run: kill
	@cd $(BACKEND_DIR) && . $(VENV_NAME)/bin/activate ; uvicorn app.main:app --reload & \
	sleep 2 && echo '\n- - - - - - - - - - - - - -' && \
	cd ../$(FRONTEND_DIR) && npm run dev

lint:
	@cd $(BACKEND_DIR) && . $(VENV_NAME)/bin/activate && \
	echo "Running imports sorting..." && \
	ruff check --select I . --fix && \
	echo "Running linting..." && \
	ruff check . --fix && \
	echo "Running formatting..." && \
	ruff format . && \
	echo "Running type checking..." && \
	mypy --config-file=pyproject.toml . && \
	cd ../$(FRONTEND_DIR) && \
	echo "Running frontend formatting..." && \
	npm run format && \
	echo "Running frontend linting..." && \
	npm run lint


help:
	@echo "Makefile commands:"
	@echo "  install:   Create virtual environment, compile requirements, install dependencies, and install pre-commit hooks."
	@echo "  run:       Run the application using uvicorn & npm (after freeing required ports)."
	@echo "  kill:      Free required ports (8000, 5173, 5678) by killing processes using them."
	@echo "  lint:      Run import sorting, linting, formatting, and type checking
	@echo "  help:      Display this help message."

.PHONY: install run kill lint help
