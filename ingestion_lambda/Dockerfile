FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY lambda_function.py /
COPY call_lambda.sh /

ENTRYPOINT [ "/bin/bash", "/call_lambda.sh" ]