# 1- Python Version that this was built on
FROM python:3.11-slim

# 2- Setting my working directory
WORKDIR /app

# 3-Pre Requirements --> libgomp1 for scikit-image/tifffile, Wine to run incostem.exe (Windows binary)
RUN dpkg --add-architecture i386 \
    && apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    wine \
    wine32 \
    && rm -rf /var/lib/apt/lists/*

# Suppress Wine debug noise and pre-initialise the Wine prefix at build time
ENV WINEDEBUG=-all
RUN wine wineboot --init 2>/dev/null || true


# 4-Requirements to install
COPY requirements.txt .


#5-Install all dependencies (torch CPU-only index is declared inside requirements.txt)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#6-copy files --> to container 
COPY . .

#7-Set output path for Docker 
ENV OUTPUT_DIR=/output

#8-Expose the port for the Dash app
EXPOSE 8050

#9-run the app
CMD ["python", "main.py"]
