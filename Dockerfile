# קובץ Docker לפריסה בענן
# זה אומר למחשב איך לבנות את האפליקציה שלנו

# משתמש בגרסת Python 3.11
FROM python:3.11-slim

# מגדיר את התיקייה שבה האפליקציה תרוץ
WORKDIR /app

# מעתיק את קובץ הדרישות
COPY requirements.txt .

# מתקין את כל הספריות הנדרשות
RUN pip install --no-cache-dir -r requirements.txt

# מעתיק את כל הקבצים של האפליקציה
COPY . .

# מגדיר משתנה סביבה
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=4000

# פותח פורט 4000
EXPOSE 4000

# מריץ את האפליקציה עם gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app 