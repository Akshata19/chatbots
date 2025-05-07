# 1. Base image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy & install python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 4. Copy your entire bot source
COPY . .

# train a brand‑new model inside the image
RUN rasa train --no-prompt

# keep only the newest model so the right one is always chosen
RUN ls -t models | tail -n +2 | xargs -r rm --

# 5. Expose Rasa’s port
EXPOSE 5005
