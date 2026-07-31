FROM python:3.10-slim-bullseye AS base

WORKDIR /app

# Install native C++ build tools & audio libraries for Librosa & C++ DSP
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    cmake \
    make \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Compile native C++ DSP shared library
RUN g++ -O3 -shared -fPIC -o app/core/libnative_dsp.so app/core/native_dsp.cpp

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
