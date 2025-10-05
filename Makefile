UV := uv
VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python
FASTAPI_PORT := 8000
VUE_PORT := 5173
DEBUG_PORT := 5678


install:
	@cd back && $(UV) venv $(VENV_NAME) && \
	. $(VENV_NAME)/bin/activate && \
	$(UV) pip compile pyproject.toml --extra dev -o requirements.txt && \
	$(UV) pip install -r requirements.txt && \
	pre-commit install && \
	cd ../front && \
	npm install

kill:
	@echo "Freeing required ports: $(FASTAPI_PORT) $(VUE_PORT) $(DEBUG_PORT)...\n"; \
	pids=$$(lsof -t -i:$(FASTAPI_PORT) -i:$(DEBUG_PORT) -i:$(VUE_PORT) 2>/dev/null); \
	if [ -n "$$pids" ]; then \
	  echo "Killing processes: $$pids"; \
	  kill -9 $$pids; \
	fi

run: kill
	@cd back && . $(VENV_NAME)/bin/activate ; uvicorn app.main:app --reload & \
	sleep 2 && echo '\n- - - - - - - - - - - - - -' && \
	cd ../front && npm run dev

help:
	@echo "Makefile commands:"
	@echo "  install:   Create virtual environment, compile requirements, install dependencies, and install pre-commit hooks."
	@echo "  run:       Run the application using uvicorn & npm (after freeing required ports)."
	@echo "  help:      Display this help message."

.PHONY: install run kill help
