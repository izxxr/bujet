# Bujet
Backend server for Bujet, a simple finance tracker.

## Usage
To run the server, **Python 3.9 or higher** is needed.

Clone this repository:

```shell
$ git clone https://github.com/izxxr/bujet.git
```

In the cloned directory, run the following command to install the dependencies.

```shell
$ pip install -r requirements.txt
```

Run the FastAPI development server using:

```shell
$ fastapi dev app.py
```

## Testing
The API routes tests are included under `tests/` directory. To run them, `pytest`
must be installed first.

```shell
$ pip install -U pytest
```

Run the tests using:

```shell
$ pytest
```
