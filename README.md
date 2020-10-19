# dashsearchupsert
## local run
* create `.env` file , in `app` folder , with odbc string, see .env.template
* docker build -t loc-dashsearchupsert .
* docker run --rm -p 8888:8888 --volume ${PWD}/app:/app loc-dashsearchupsert python3 /app/app.py
* open in chrome: http://localhost:8888
