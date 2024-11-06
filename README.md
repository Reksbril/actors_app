## Development

### Setup
To setup local environment, run following script

```
scripts/setup_env.sh
```

It will create virtual env, install requirements, setup database and other dependencies. For the development purposes activate the virtual env

```
source .venv/bin/activate
```

### Start debug server

```
python manage.py runserver
```

### Testing

```
python manage.py test
```
