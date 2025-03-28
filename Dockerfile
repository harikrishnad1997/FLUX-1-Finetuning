# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt 
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Streamlit
RUN pip install streamlit

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8510 available to the world outside this container
EXPOSE 8510

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.port", "8510", "--server.address=0.0.0.0"]