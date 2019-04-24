FROM ubuntu:14.04

# Update OS
RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade

# Install Python
RUN apt-get install -y python-dev python-pip

# Set default directory for our application
WORKDIR /app

# Add requirements.txt
ADD requirements.txt /app

# Install uwsgi Python web server
RUN pip install uwsgi

# Upgrade pip to 9.0.1
RUN pip install -U pip

# Install app requirements
RUN pip install --ignore-installed -r requirements.txt

# Create app directory
COPY . /app

# Set the environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS multi-user-dungeon-firebase-adminsdk-fi2hw-4a23306b15.json

# Expose port 8000 for uwsgi
EXPOSE 8000

#create a directory for logs
RUN mkdir /app/logs

ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--module", "app:app", "--processes", "4", "--threads", "4"]
