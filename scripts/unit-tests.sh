pip install -r ./requirements.txt
coverage run -a --source=.  -m pytest .
coverage report
coverage html
