# TODO Fill with Dockerfile instructions to build your image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents writing bytecode files to disk
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /kurtosis

# Install system dependencies (e.g., if you need database libraries or other system tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . /kurtosis

# env variables to be provided through Docker CLI.
ENV INPUT_PATH='/kurtosis/input/test_input.yaml'
ENV OUTPUT_PATH='/kurtosis/output/test_output.txt'

# Specify the command to run on container start
#CMD ["sh", "-c", "python /kurtosis/app/scheduler.py -i ${INPUT_PATH} -o ${OUTPUT_PATH}"]
ENTRYPOINT ["python", "/kurtosis/app/scheduler.py"]
