# Installation

## Docker
A ready-to-use docker image is available on [Docker Hub](https://hub.docker.com/r/ltrezzini/franceocr-api/).
Once docker and docker-compose are installed, you can launch the service using `docker-compose up -d`.
The service is then available on `http://localhost:5000`. It is recommended to serve this API using an HTTPS reverse proxy.

## System
If you can't use docker, it is possible to run this service directly on the host system.
You will have to compile and install all the dependencies with the correct versions.
You can follow the detailed procedure available in `Dockerfile` (archlinux base image) and `Dockerfile_centos` (centos base image).

### Dependencies
The service requires the following libraries, with their own dependencies installed:
- python>=3.5
- numpy>=1.10
- opencv>=3
- [tesseract>=4](https://github.com/tesseract-ocr/tesseract/wiki/Compiling)

All python dependencies are listed in the `requirements.txt` file.
You can install them using `pip install -r requirements.txt`.

### Running
For security and performance reasons, you should use a WSGI server to run the python API.
We recommand to use `gunicorn`.

The following command should do the trick:
`gunicorn --config api/gunicorn.conf --log-config api/logging.conf -b :5000 --chdir api server:server`.

As the API is stateless and doesn't require any database or external service, there are no specific tasks or conditions
to start or stop the service.

### Logging
All the logs are outputed at WARNING level to STDOUT in JSON format.
You should edit `logging.conf` if you want to alter this behavior.
