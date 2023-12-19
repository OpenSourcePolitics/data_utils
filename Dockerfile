FROM python:3.11-buster

ENV METABASE_HOST="https://metabase.example.com" \
    METABASE_USERNAME="user@example.com" \
    METABASE_PASSWORD='user_password' \
    ROCKETCHAT_USERNAME="user@example.com" \
    ROCKETCHAT_PASSWORD="user_password" \
    ROCKETCHAT_URL="https://rocket.chat.example"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install Poetry
RUN pip install poetry

# Copy your project's pyproject.toml and optionally poetry.lock file
COPY pyproject.toml poetry.lock* /usr/src/app/

# Disable virtualenv creation from poetry as it is not needed in Docker
# and install the dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of your application's code
COPY . /usr/src/app

# Command to run the application
CMD ["poetry", "run", "query_checker", "Démo"]
