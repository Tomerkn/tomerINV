# קובץ Docker לפריסה בענן
# זה אומר למחשב איך לבנות את האפליקציה שלנו

# משתמש בגרסת Python 3.11
FROM python:3.11-slim

# מגדיר את התיקייה שבה האפליקציה תרוץ
WORKDIR /app

# מתקין Flask בלבד לבדיקה
RUN pip install flask

# מעתיק את האפליקציה הפשוטה
COPY simple_test_app.py app.py

# מגדיר משתנה סביבה
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=4000

# פותח פורט 4000
EXPOSE 4000

# מריץ את האפליקציה הפשוטה
CMD python app.py 