
virtualenv:
	rm -rf venv
	virtualenv venv --distribute
	sh -c "source venv/bin/activate && pip install -r requirements.txt"

devserver:
	IMGFAB_DEBUG=1 python flaskapp/app.py

devworker:
	mrq-worker highpriority default 3d  --greenlets 5

herokuvi:
	curl https://s3.amazonaws.com/heroku-jvm-buildpack-vi/vim-7.3.tar.gz --output vim.tar.gz
	mkdir vim && tar xzf vim.tar.gz -C vim
	ln -s vim/bin/vim vi
	rm vim.tar.gz