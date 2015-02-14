
virtualenv:
	rm -rf venv
	virtualenv venv --distribute
	sh -c "source venv/bin/activate && pip install -r requirements.txt"
