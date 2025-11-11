FROM python:3.11-slim
WORKDIR /app

# System deps for docx2pdf/LibreOffice (optional). Comment out if not needed.
RUN apt-get update && apt-get install -y libreoffice default-libmysqlclient-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
