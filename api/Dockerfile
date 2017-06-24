# start with a base image
FROM base/archlinux

RUN pacman -Sy
RUN pacman -S --needed --noconfirm opencv python-numpy eigen
RUN pacman -S --needed --noconfirm python-pip
RUN pacman -S --needed --noconfirm git gcc make cmake pkg-config pango cairo icu
RUN pacman -S --needed --noconfirm leptonica

# Install tesseract
RUN git clone https://github.com/tesseract-ocr/tesseract.git /deps/tesseract
RUN mkdir -p /deps/tesseract/build
WORKDIR /deps/tesseract/build
RUN cmake .. && make
RUN make install

# Install official lang data
# RUN

RUN groupadd python && useradd --create-home --home-dir /home/python -g python python

RUN mkdir /app && chown python /app && chmod 700 /app

COPY . /app
WORKDIR /app

# Install trained lang data
RUN cp franceocr.traineddata /usr/local/share/tessdata

# Install python dependencies
RUN pip install -U -r requirements.txt

USER python

EXPOSE 5000
CMD ["python", "server.py"]
