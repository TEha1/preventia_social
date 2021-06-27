# preventia_social

### Clone the project

You just need to open terminal

```sh
$ git clone https://github.com/TEha1/preventia_social.git
$ cd preventia_social
```

### Create and activate python environment

You can check that out [Creation of virtual environments](https://docs.python.org/3/library/venv.html#module-venv).

```sh
$ python3 -m venv env
$ source env/bin/activate
```

### Install requirements

You can check that out [pip install](https://pip.pypa.io/en/stable/cli/pip_install/#pip-install).

```sh
$ pip install -r requirements
```

### Run the project

```sh
# prepare the project
$ python manage.py migrate
$ python manage.py collectstatic
# run the project
$ python manage.py runserver
```

### Test Cases
```sh
# run the endpoints test cases
$ python manage.py test
```

## EndPoints:

- Login to the admin from this link (http://127.0.0.1:8000/admin/) using these credentials:
     - ``username: admin / password: admin``
- Then you can check the swagger from this link (http://127.0.0.1:8000/swagger/)
- Then you can download the swagger schema from this links:
     - (http://127.0.0.1:8000/swagger.json) or (http://127.0.0.1:8000/swagger.yaml)