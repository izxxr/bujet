# Bujet
Backend server for Bujet, a simple finance tracker.

## Usage
To run the server, **Python 3.9 or higher** is needed.

Clone this repository:

```shell
$ git clone https://github.com/izxxr/bujet.git
```

### Installation
In the cloned directory, run the following command to install the dependencies.

```shell
$ pip install -r requirements.txt
```

### Generating Encryption Key
Bujet uses `cryptography.Fernet` encryption for storing sensitive information in
database. This requires a Fernet encryption key to be generated and provided in
`BUJET_ENCRYPTION_KEY` environment variable.

In order to generate a Fernet encryption key, you can use `cryptography.Fernet.generate_key()`
method as shown in the following Python code:

```py
from cryptography.fernet import Fernet

print("Encryption key: ", Fernet.generate_key())
```

The generated key must be provided through the environment variables. Create a `.env`
file and provide the encryption key:

```bash
BUJET_ENCRYPTION_KEY="put encryption key here"
```

### Running the Server
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
