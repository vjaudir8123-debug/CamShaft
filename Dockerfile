FROM python:3.10-slim

# Install git and required system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the CamShaft SDK globally
COPY . /app
RUN pip install --no-cache-dir -e .

# By default, open a bash shell so the user can interact with the SDK
CMD ["bash"]
