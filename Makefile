
virtualenv:
	rm -rf venv
	virtualenv venv --distribute
	sh -c "source venv/bin/activate && pip install -r requirements.txt"

devserver:
	IMGFAB_DEBUG=1 python flaskapp/app.py

devworker:
	mrq-worker highpriority default 3d  --greenlets 5