# Use the official Python image as the base image
FROM python:3.10.6-slim-bullseye

# Set the environment variables
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib

# Install the required system dependencies
RUN apt-get update && \
    apt-get install -y git gcc libsqlite3-dev tclsh libssl-dev libc6-dev make

# Install SQLCipher directly from the source code
RUN git clone --depth=1 --branch=master https://github.com/sqlcipher/sqlcipher.git && \
  cd sqlcipher && \
  ./configure --enable-tempstore=yes \
    CFLAGS="-DSQLITE_HAS_CODEC" LDFLAGS="-lcrypto -lsqlite3" && \
  make && \
  make install

# Copy the main.py script into the container
COPY main.py /app/main.py

# Install the required Python libraries
RUN pip install pysqlcipher3==1.2.0

# Set the working directory to /app
WORKDIR /app

# Run the Python script by default when the container is started
ENTRYPOINT ["python", "main.py"]
