# LibreTranslate Local Setup Guide

This guide provides instructions on how to set up LibreTranslate on your local machine. LibreTranslate is a free and open-source machine translation API, powered by Argos Translate.

## Table of Contents

1.  [Prerequisites](#prerequisites)
2.  [Setup Methods](#setup-methods)
    *   [Method 1: Using Docker (Recommended)](#method-1-using-docker-recommended)
    *   [Method 2: From Source](#method-2-from-source)
    *   [Method 3: Using Docker Compose (for multiple services)](#method-3-using-docker-compose-for-multiple-services)
3.  [Configuration](#configuration)
    *   [Environment Variables](#environment-variables)
    *   [Language Models](#language-models)
4.  [Usage](#usage)
    *   [Accessing the Web UI](#accessing-the-web-ui)
    *   [API Endpoints](#api-endpoints)
5.  [Troubleshooting](#troubleshooting)
6.  [Contributing](#contributing)
7.  [License](#license)

---

## 1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Git:** For cloning the repository.
    *   [Download Git](https://git-scm.com/downloads)
*   **Python 3.8+** (Required for "From Source" method)
    *   [Download Python](https://www.python.org/downloads/)
*   **pip** (Python package installer, usually comes with Python)
*   **Docker** (Required for "Using Docker" and "Using Docker Compose" methods)
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## 2. Setup Methods

Choose the method that best suits your needs. Docker is generally recommended for ease of setup and dependency management.

### Method 1: Using Docker (Recommended)

This is the quickest and easiest way to get LibreTranslate running.

1.  **Pull the Docker image:**
    ```bash
    docker pull libretranslate/libretranslate
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -it --rm -p 5000:5000 libretranslate/libretranslate
    ```
    *   `-it`: Runs in interactive mode and allocates a pseudo-TTY.
    *   `--rm`: Automatically removes the container when it exits.
    *   `-p 5000:5000`: Maps port 5000 on your host machine to port 5000 inside the container. You can change the host port if 5000 is already in use (e.g., `-p 8000:5000`).

3.  **Verify installation:**
    Open your web browser and navigate to `http://localhost:5000`. You should see the LibreTranslate web interface.

### Method 2: From Source

This method gives you more control over the environment and is useful for development or custom configurations.

1.  **Clone the LibreTranslate repository:**
    ```bash
    git clone https://github.com/LibreTranslate/LibreTranslate.git
    cd LibreTranslate
    ```

2.  **Create and activate a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download language models:**
    LibreTranslate uses Argos Translate models. You'll need to download the models for the languages you want to support.
    ```bash
    # Example: Download English-Spanish and Spanish-English models
    python3 -m libretranslate download en es
    ```
    You can download multiple models at once:
    ```bash
    python3 -m libretranslate download en es fr de
    ```
    To see available models:
    ```bash
    python3 -m libretranslate --help
    ```

5.  **Run LibreTranslate:**
    ```bash
    python3 -m libretranslate
    ```
    By default, it will run on `http://localhost:5000`.

6.  **Verify installation:**
    Open your web browser and navigate to `http://localhost:5000`.

### Method 3: Using Docker Compose (for multiple services)

If you plan to run LibreTranslate alongside other services (e.g., a database, a frontend application), Docker Compose is an excellent choice.

1.  **Clone the LibreTranslate repository:**
    ```bash
    git clone https://github.com/LibreTranslate/LibreTranslate.git
    cd LibreTranslate
    ```

2.  **Create a `docker-compose.yml` file** in the root of the `LibreTranslate` directory (or a new directory for your project) with the following content:

    ```yaml
    version: '3.8'

    services:
      libretranslate:
        image: libretranslate/libretranslate
        container_name: libretranslate_server
        ports:
          - "5000:5000"
        environment:
          # Optional: Configure API key, update interval, etc.
          # See "Configuration" section for more details
          # LT_API_KEY: "your_secret_api_key"
          # LT_UPDATE_MODELS: "true"
          # LT_HOST: "0.0.0.0"
          # LT_PORT: "5000"
        volumes:
          # Optional: Persist downloaded models
          - ./models:/app/models
        restart: unless-stopped
    ```

3.  **Start the services:**
    ```bash
    docker-compose up -d
    ```
    *   `-d`: Runs the containers in detached mode (in the background).

4.  **Verify installation:**
    Open your web browser and navigate to `http://localhost:5000`.

5.  **Stop the services:**
    ```bash
    docker-compose down
    ```

---

## 3. Configuration

LibreTranslate can be configured using environment variables.

### Environment Variables

You can set these variables before running LibreTranslate (for source setup) or pass them to the Docker container/Docker Compose service.

| Variable Name        | Description