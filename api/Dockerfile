# start with a base image
FROM base/archlinux

RUN pacman -Sy
RUN pacman -S --needed --noconfirm opencv python-numpy eigen
RUN pacman -S --needed --noconfirm python-pip
RUN pacman -S --needed --noconfirm git autoconf-archive automake pkg-config pango-devel cairo-devel icu-devel

# Install tesseract
RUN git clone https://github.com/tesseract-ocr/tesseract.git /deps/tesseract
WORKDIR /deps/tesseract
RUN mkdir build && cd build
RUN cmake .. && make
RUN make install

# Install official lang data
# RUN

RUN groupadd python && useradd --create-home --home-dir /home/python -g python python

RUN mkdir /app && chown python /app && chmod 700 /app

WORKDIR /app
COPY . /app

# Install trained lang data
RUN cp training/franceocr.traineddata $TESSDATA_PREFIX

# Install python dependencies
RUN pip install -U -r requirements.txt

USER python

EXPOSE 5000
CMD ["python", "server.py"]
