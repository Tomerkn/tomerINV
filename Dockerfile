# קובץ Docker לפריסה בענן
# זה אומר למחשב איך לבנות את האפליקציה שלנו

# משתמש בגרסת Python 3.11
FROM python:3.11-slim

# מגדיר את התיקייה שבה האפליקציה תרוץ
WORKDIR /app

# מעתיק את קובץ requirements.txt
COPY requirements.txt .

# מתקין את כל הספריות שצריך
RUN pip install --no-cache-dir -r requirements.txt

# מעתיק את כל הקבצים של האפליקציה
COPY . .

# מגדיר משתנה סביבה
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# פותח פורט 4000
EXPOSE 4000

# מגדיר את הפקודה שרצה כשהאפליקציה מתחילה
# עם timeout של 30 שניות ו-4 workers
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "--timeout", "30", "--workers", "4", "--preload", "app:app"] 