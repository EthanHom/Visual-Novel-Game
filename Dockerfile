# official python 3.11 base image
FROM python:3.11-slim

# install bash and sqlite3
RUN apt-get update && \
    apt-get install -y bash sqlite3 zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /workspace

# install Python packages
RUN pip install --no-cache-dir pandas SQLAlchemy

# copy project files (unnecessary if mounting directory)
# COPY . /workspace

# default to bash shell on start
CMD ["bash"]