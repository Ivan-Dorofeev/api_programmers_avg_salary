# api_programmers_avg_salary

Parsing HeadHunter и SuperJob and get average salary of the most populat programming languages.



## Install

First of all, install packages from requirements.txt:

python pip -m install -r requirements.txt

Then you need to create file ".env" and add variable:

> SUPERJOB_SECRET_KEY = [....your secret_key...]


Script take values of this variables and use:

> headers = {'X-Api-App-Id': os.environ['SUPERJOB_SECRET_KEY']}

```For more information or to get secret_key read:``` https://api.superjob.ru/

## Run

Open console in working directory and write:

```python main.py```

result:

