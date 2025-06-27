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

# מגדיר הרשאות לסקריפט הפעלה
RUN chmod +x start.sh

# מגדיר משתנה סביבה
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# פותח פורט 8080
EXPOSE 8080

# מגדיר את הפקודה שרצה כשהאפליקציה מתחילה
CMD ["./start.sh"] 