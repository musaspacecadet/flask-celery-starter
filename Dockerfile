FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy Supervisor configuration file
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]