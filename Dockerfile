# Base image
FROM python:3.9-alpine

# add required packages
RUN \
    apk add --no-cache \
        bluez \
        git

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/aso824/yeehack.git

# Set the working directory to the cloned repository
WORKDIR /app/yeehack

# Install requirements
RUN pip install -r requirements.txt

# Set the command to run the server.py file with the specified port
CMD python yeehack.py server
