#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט להעברת נתונים ממסד הנתונים המקומי למסד הנתונים בענן
"""

import sqlite3
import psycopg2
import os

# פה אני מגדיר את שם קובץ מסד הנתונים המקומי
LOCAL_DB = 'investments.db'  # זה הקובץ המקומי

# פה אני לוקח את כתובת מסד הנתונים בענן מהסביבה (צריך להגדיר DATABASE_URL)
CLOUD_DB_URL = os.getenv('DATABASE_URL')  # משתנה סביבה עם הכתובת

# פונקציה שמביאה את כל הנתונים מהטבלה המקומית
def get_local_data():
    """מחזירה את כל הנתונים מהטבלה המקומית"""
    conn = sqlite3.connect(LOCAL_DB)  # פותח חיבור למסד המקומי
    cursor = conn.cursor()
    cursor.execute('SELECT name, symbol, price, type FROM securities')
    data = cursor.fetchall()  # מביא את כל השורות
    conn.close()  # סוגר את החיבור
    return data

# פונקציה שמכניסה את כל הנתונים למסד בענן
def insert_to_cloud(data):
    """מכניסה את כל הנתונים למסד בענן"""
    conn = psycopg2.connect(CLOUD_DB_URL)  # פותח חיבור למסד בענן
    cursor = conn.cursor()
    for row in data:
        # מוסיף כל שורה לטבלה בענן
        cursor.execute(
            'INSERT INTO securities (name, symbol, price, type) VALUES (%s, %s, %s, %s)',
            row
        )
    conn.commit()  # שומר את כל השינויים
    conn.close()  # סוגר את החיבור
    print('סיימתי להעביר את כל הנתונים לענן!')

# אם מריצים את הקובץ הזה ישירות – תבצע את ההעברה
if __name__ == '__main__':
    print('מתחיל להעביר נתונים מהמסד המקומי לענן...')
    data = get_local_data()  # מביא את כל הנתונים מהמקומי
    print(f'יש {len(data)} שורות להעביר')
    insert_to_cloud(data)  # מכניס הכל לענן 