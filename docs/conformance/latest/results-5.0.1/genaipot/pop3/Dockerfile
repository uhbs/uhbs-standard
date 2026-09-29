# UHBS 5.0.1 score Dockerfile — unit `genaipot-pop3`
# Source: .local/labs/genaipot/Dockerfile
# Target image: annls/genaipot:latest (sha256:627d7fde6d4a6f937fde3b3366fb55605a90cea6370e1f5beac9c39d8ecfeeac)
# Rebuild (build context = cloned upstream under .local/labs/genaipot):
#   docker build -f Dockerfile -t annls/genaipot:latest .local/labs/genaipot
# Exact image without rebuild (see Dockerfile.pin):
#   docker build -f Dockerfile.pin -t annls/genaipot:latest .
#
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 25 (SMTP) and port 110 (POP3) available to the world outside this container
EXPOSE 25 110

# Run main.py when the container launches
CMD ["/app/start.sh"]
