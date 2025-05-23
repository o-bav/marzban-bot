# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
# This assumes the Dockerfile is in the telegram_bot directory.
# So, '.' refers to the telegram_bot directory on the host.
COPY . .

# Set the command to run the application
CMD ["python", "bot.py"]
