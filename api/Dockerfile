# start with a base image
FROM base/archlinux

RUN pacman -Sy
RUN pacman -S --needed --noconfirm opencv python-numpy eigen
RUN pacman -S --needed --noconfirm python-pip
RUN pacman -S --needed --noconfirm git gcc make cmake pkg-config pango cairo icu
RUN pacman -S --needed --noconfirm leptonica hdf5

# Install tesseract
RUN git clone https://github.com/tesseract-ocr/tesseract.git /deps/tesseract
RUN mkdir -p /deps/tesseract/build
WORKDIR /deps/tesseract/build
RUN cmake .. && make
RUN make install

RUN groupadd python && useradd --create-home --home-dir /home/python -g python python

RUN mkdir /app && chown python:python /app && chmod 700 /app
RUN mkdir /uploads && chown python:python /uploads && chmod 700 /uploads

USER python
ENV PATH="/usr/local/bin:${PATH}" LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib" TESSDATA_PREFIX=/usr/local/share/tessdata
EXPOSE 5000

WORKDIR /app

# Install python dependencies
COPY requirements.txt /app
RUN pip install -U -r requirements.txt

# Install trained lang data
COPY franceocr.traineddata $TESSDATA_PREFIX

COPY . /app

CMD ["python", "server.py"]
