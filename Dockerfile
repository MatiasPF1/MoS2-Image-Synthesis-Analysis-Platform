# 1- Python Version that this was built on
FROM python:3.11-slim

# 2- Setting my working directory
WORKDIR /app

# 3-Pre Requirements --> running dependencies for scikit-image and tifffile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*


# 4-Requirements to install
COPY requirements.txt .


#5-Install all dependencies (torch CPU-only index is declared inside requirements.txt)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#6-copy files --> to container 
COPY . .

#7-Create the output directory (users mount their Downloads/STEM_MOS2 folder here)
RUN mkdir -p /output
VOLUME ["/output"]

#8-Expose the port for the Dash app
EXPOSE 8050

#9-run the app
CMD ["python", "main.py"]
