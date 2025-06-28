# קובץ Docker לפריסה בענן
# זה אומר למחשב איך לבנות את האפליקציה שלנו

# משתמש בגרסת Python 3.11
FROM python:3.11-slim

# מגדיר את התיקייה שבה האפליקציה תרוץ
WORKDIR /app

# מעתיק את קובץ requirements.txt
COPY requirements.txt .

# מתקין את כל הספריות שצריך
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# מעתיק את כל הקבצים של האפליקציה
COPY . .

# מגדיר משתנה סביבה
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=4000

# פותח פורט 4000 (Railway יעביר את הפורט הנכון דרך משתנה סביבה)
EXPOSE 4000

# מגדיר את הפקודה שרצה כשהאפליקציה מתחילה
# משתמש ב-gunicorn לפריסה בענן
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 30 --workers 4 --preload app:app 