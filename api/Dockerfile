FROM base/archlinux
MAINTAINER Louis Trezzini <louis.trezzini@ponts.org>

RUN groupadd python && useradd -g python python

RUN mkdir /app && chown python:python /app && chmod 700 /app
RUN mkdir /uploads && chown python:python /uploads && chmod 700 /uploads
RUN mkdir /logs && chown python:python /logs && chmod 700 /logs

WORKDIR /app

RUN echo \
    && pacman -Sy \
    && pacman -S --needed --noconfirm opencv python-numpy hdf5 ghostscript \
    && pacman -S --needed --noconfirm python-pip gcc make autoconf-archive automake pkg-config leptonica imagemagick

RUN mkdir /deps && cd /deps && wget https://github.com/tesseract-ocr/tesseract/archive/eba0ae3b88a46a93e981770caa0b148d65cc4468.zip \
    && unzip eba0ae3b88a46a93e981770caa0b148d65cc4468.zip -d tesseract/ && cd tesseract/tesseract-eba0ae3b88a46a93e981770caa0b148d65cc4468/ \
    && ./autogen.sh && ./configure && make -j $(nproc) && make install \
    && rm -rf /deps

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PATH="/usr/local/bin:${PATH}" LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib" TESSDATA_PREFIX=/usr/local/share/tessdata

# Install trained lang data
RUN mkdir -p $TESSDATA_PREFIX
COPY franceocr.traineddata $TESSDATA_PREFIX
COPY OCRB.traineddata $TESSDATA_PREFIX

COPY . /app

USER python

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "/app/gunicorn.conf", "--log-config", "/app/logging.conf", "-b", ":5000", "server:server"]
