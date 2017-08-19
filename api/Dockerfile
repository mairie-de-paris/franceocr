FROM python:alpine3.6
MAINTAINER Louis Trezzini <louis.trezzini@ponts.org>

RUN addgroup -S python && adduser -S -g python python

RUN mkdir /app && chown python:python /app && chmod 700 /app
RUN mkdir /uploads && chown python:python /uploads && chmod 700 /uploads
RUN mkdir /logs && chown python:python /logs && chmod 700 /logs

WORKDIR /app

COPY requirements.txt requirements.txt
RUN echo \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" > /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
    && apk add --no-cache opencv libstdc++ lapack-dev \
    && apk add --no-cache --virtual .build-deps build-base git autoconf autoconf-archive automake libtool hdf5 \
    imagemagick-dev libjpeg-turbo-dev gfortran libpng-dev freetype-dev leptonica-dev \
    && pip install numpy \
    && pip install -r requirements.txt \
    && git clone https://github.com/tesseract-ocr/tesseract.git /deps/tesseract \
    && cd /deps/tesseract \
    && ./autogen.sh && ./configure && make -j $(nproc) && make install \
    && cd /app \
    && rm -r /deps \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

ENV PATH="/usr/local/bin:${PATH}" LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib" TESSDATA_PREFIX=/usr/local/share/tessdata

# Install trained lang data
RUN mkdir -p $TESSDATA_PREFIX
COPY franceocr.traineddata $TESSDATA_PREFIX
COPY OCRB.traineddata $TESSDATA_PREFIX

COPY . /app

USER python

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "/app/gunicorn.conf", "--log-config", "/app/logging.conf", "-b", ":5000", "server:server"]
