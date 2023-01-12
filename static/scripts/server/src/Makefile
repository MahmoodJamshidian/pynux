PYTHON=python3.11
VENV_ACTIVATOR=../../../../venv/bin/activate
SETUP_FILE=setup.py
SETUP_ARGS=build_ext --inplace

compile: activate
	$(PYTHON) $(SETUP_FILE) $(SETUP_ARGS)

activate:
	@echo activating virtual environment ...
	@echo virtualenv activator path: $(VENV_ACTIVATOR)
	@. $(VENV_ACTIVATOR)
	@echo virtualenv activated

deactivate:
	@deactivate

clean:
	@rm -rf main.cpp build