# start with a base image
FROM base/archlinux

RUN pacman -Sy
RUN pacman -S --needed --noconfirm tesseract opencv python-numpy eigen
RUN pacman -S --needed --noconfirm tesseract-data-eng tesseract-data-fra
RUN pacman -S --needed --noconfirm python-pip

RUN groupadd python && useradd --create-home --home-dir /home/python -g python python

RUN mkdir /app && chown python /app && chmod 700 /app
WORKDIR /app/src

COPY requirements.txt .
RUN pip install -U -r requirements.txt

USER python

EXPOSE 5000
CMD ["python", "app.py"]
