PYTHON=python3.11
VENV_ACTIVATOR=../../../../venv/bin/activate
BUILD_DIR=../
SETUP_FILE=setup.py
SETUP_ARGS=build_ext --inplace

compile: activate
	$(PYTHON) $(SETUP_FILE) $(SETUP_ARGS)
	@echo compile completed

build: compile clean
	cp *.so $(BUILD_DIR)
	cp .env $(BUILD_DIR)
	@echo build completed

activate:
	@echo activating virtual environment ...
	@echo virtualenv activator path: $(VENV_ACTIVATOR)
	@. $(VENV_ACTIVATOR)
	@echo virtualenv activated

clean:
	@rm -rf main.cpp build