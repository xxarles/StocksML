
FROM python:3.12-slim


# Add Docker's official GPG key:
RUN apt-get update && apt-get install ca-certificates curl -y \
    && install -m 0755 -d /etc/apt/keyrings\
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc\
    && chmod a+r /etc/apt/keyrings/docker.asc
    
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
WORKDIR /app
COPY stocks_backend stocks_backend
COPY stocks_metadata stocks_metadata
COPY manage.py manage.py
COPY docker_startup.sh docker_startup.sh
COPY pytest.ini pytest.ini

ENTRYPOINT [ "/bin/bash", "/app/docker_startup.sh" ]