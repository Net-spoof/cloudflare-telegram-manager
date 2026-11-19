FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -r -u 10001 -m botuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py auth_check.py i18n.py locales.json ./
RUN mkdir -p /app/data && chown -R botuser:botuser /app
USER botuser
CMD ["python", "bot.py"]
