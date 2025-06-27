#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט להזרקת נתונים ישירות למסד הנתונים בענן
מתחבר ל-PostgreSQL בענן ומוסיף נתוני דוגמה
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import logging

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """מחזיר את כתובת מסד הנתונים מהסביבה"""
    # בדיקה אם יש DATABASE_URL מוגדר
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        logger.info(f"נמצא DATABASE_URL: {db_url[:20]}...")
        return db_url
    
    # אם לא, ננסה לקחת מהמשתמש
    logger.warning("לא נמצא DATABASE_URL, נצטרך להגדיר ידנית")
    return None

def create_tables(conn):
    """יוצר את הטבלאות הנדרשות"""
    try:
        cursor = conn.cursor()
        
        # יצירת טבלת ניירות ערך
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS securities (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                sector VARCHAR(50),
                price DECIMAL(10,2),
                change_percent DECIMAL(5,2),
                volume BIGINT,
                market_cap DECIMAL(15,2),
                pe_ratio DECIMAL(8,2),
                dividend_yield DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # יצירת טבלת השקעות
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                shares INTEGER NOT NULL,
                purchase_price DECIMAL(10,2) NOT NULL,
                purchase_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES securities(symbol)
            )
        """)
        
        # יצירת טבלת משתמשים
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("טבלאות נוצרו בהצלחה")
        return True
        
    except Exception as e:
        logger.error(f"שגיאה ביצירת טבלאות: {e}")
        conn.rollback()
        return False

def insert_sample_securities(conn):
    """מוסיף ניירות ערך לדוגמה"""
    try:
        cursor = conn.cursor()
        
        # נתוני ניירות ערך לדוגמה
        securities_data = [
            ('AAPL', 'Apple Inc.', 'Technology', 150.25, 2.5, 50000000, 2500000000000, 25.5, 0.6),
            ('MSFT', 'Microsoft Corporation', 'Technology', 320.75, 1.8, 30000000, 2400000000000, 30.2, 0.8),
            ('GOOGL', 'Alphabet Inc.', 'Technology', 2800.50, 3.2, 20000000, 1800000000000, 28.1, 0.0),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 3300.25, -1.2, 25000000, 1600000000000, 45.3, 0.0),
            ('TSLA', 'Tesla Inc.', 'Automotive', 850.75, 5.8, 40000000, 800000000000, 120.5, 0.0),
            ('NVDA', 'NVIDIA Corporation', 'Technology', 450.30, 4.1, 35000000, 1100000000000, 35.2, 0.2),
            ('META', 'Meta Platforms Inc.', 'Technology', 280.90, 2.7, 28000000, 750000000000, 22.8, 0.0),
            ('BRK.A', 'Berkshire Hathaway Inc.', 'Financial', 450000.00, 0.8, 1000, 650000000000, 15.5, 0.0),
            ('JNJ', 'Johnson & Johnson', 'Healthcare', 165.40, 1.2, 15000000, 400000000000, 18.3, 2.8),
            ('V', 'Visa Inc.', 'Financial', 240.60, 2.1, 20000000, 500000000000, 32.1, 0.7),
            ('JPM', 'JPMorgan Chase & Co.', 'Financial', 140.80, 1.5, 25000000, 420000000000, 12.8, 2.9),
            ('PG', 'Procter & Gamble Co.', 'Consumer Staples', 145.20, 0.9, 12000000, 350000000000, 24.6, 2.4),
            ('HD', 'Home Depot Inc.', 'Consumer Discretionary', 320.45, 2.3, 18000000, 380000000000, 22.1, 2.1),
            ('DIS', 'Walt Disney Co.', 'Communication Services', 95.30, -0.8, 22000000, 170000000000, 45.2, 0.0),
            ('NFLX', 'Netflix Inc.', 'Communication Services', 480.75, 3.4, 15000000, 210000000000, 35.8, 0.0),
            ('CRM', 'Salesforce Inc.', 'Technology', 220.90, 2.6, 20000000, 220000000000, 85.3, 0.0),
            ('ADBE', 'Adobe Inc.', 'Technology', 380.25, 1.9, 12000000, 180000000000, 42.1, 0.0),
            ('PYPL', 'PayPal Holdings Inc.', 'Financial', 180.60, 2.8, 25000000, 210000000000, 28.5, 0.0),
            ('INTC', 'Intel Corporation', 'Technology', 45.80, -1.2, 35000000, 190000000000, 12.3, 3.2),
            ('CSCO', 'Cisco Systems Inc.', 'Technology', 48.90, 1.1, 28000000, 200000000000, 15.8, 3.1),
            ('PFE', 'Pfizer Inc.', 'Healthcare', 42.30, 0.7, 30000000, 240000000000, 8.9, 4.2),
            ('KO', 'Coca-Cola Co.', 'Consumer Staples', 58.75, 1.3, 20000000, 250000000000, 24.1, 3.1),
            ('PEP', 'PepsiCo Inc.', 'Consumer Staples', 165.40, 1.6, 15000000, 230000000000, 25.8, 2.8),
            ('ABT', 'Abbott Laboratories', 'Healthcare', 110.20, 2.1, 18000000, 190000000000, 22.3, 1.8),
            ('TMO', 'Thermo Fisher Scientific Inc.', 'Healthcare', 520.80, 2.9, 8000000, 210000000000, 35.6, 0.3),
            ('UNH', 'UnitedHealth Group Inc.', 'Healthcare', 480.30, 1.8, 12000000, 440000000000, 22.1, 1.4)
        ]
        
        # הכנסת הנתונים
        for security in securities_data:
            cursor.execute("""
                INSERT INTO securities (symbol, name, sector, price, change_percent, volume, market_cap, pe_ratio, dividend_yield)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    sector = EXCLUDED.sector,
                    price = EXCLUDED.price,
                    change_percent = EXCLUDED.change_percent,
                    volume = EXCLUDED.volume,
                    market_cap = EXCLUDED.market_cap,
                    pe_ratio = EXCLUDED.pe_ratio,
                    dividend_yield = EXCLUDED.dividend_yield
            """, security)
        
        conn.commit()
        logger.info(f"הוספו {len(securities_data)} ניירות ערך למסד הנתונים")
        return True
        
    except Exception as e:
        logger.error(f"שגיאה בהוספת ניירות ערך: {e}")
        conn.rollback()
        return False

def insert_sample_investments(conn):
    """מוסיף השקעות לדוגמה"""
    try:
        cursor = conn.cursor()
        
        # נתוני השקעות לדוגמה
        investments_data = [
            (1, 'AAPL', 100, 145.50, '2024-01-15'),
            (1, 'MSFT', 50, 300.25, '2024-02-20'),
            (1, 'GOOGL', 25, 2700.00, '2024-03-10'),
            (1, 'TSLA', 30, 800.00, '2024-01-30'),
            (1, 'NVDA', 40, 420.75, '2024-02-15'),
            (1, 'META', 60, 260.50, '2024-03-05'),
            (1, 'AMZN', 35, 3200.00, '2024-01-25'),
            (1, 'JNJ', 80, 160.00, '2024-02-10'),
            (1, 'V', 45, 235.00, '2024-03-01'),
            (1, 'HD', 25, 310.00, '2024-01-20')
        ]
        
        # הכנסת הנתונים
        for investment in investments_data:
            cursor.execute("""
                INSERT INTO investments (user_id, symbol, shares, purchase_price, purchase_date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, investment)
        
        conn.commit()
        logger.info(f"הוספו {len(investments_data)} השקעות למסד הנתונים")
        return True
        
    except Exception as e:
        logger.error(f"שגיאה בהוספת השקעות: {e}")
        conn.rollback()
        return False

def insert_sample_user(conn):
    """מוסיף משתמש לדוגמה"""
    try:
        cursor = conn.cursor()
        
        # משתמש לדוגמה (סיסמה: password123)
        cursor.execute("""
            INSERT INTO users (username, password_hash, email)
            VALUES ('demo_user', 'pbkdf2:sha256:600000$demo_hash$password123', 'demo@example.com')
            ON CONFLICT (username) DO NOTHING
        """)
        
        conn.commit()
        logger.info("משתמש לדוגמה נוסף בהצלחה")
        return True
        
    except Exception as e:
        logger.error(f"שגיאה בהוספת משתמש: {e}")
        conn.rollback()
        return False

def main():
    """הפונקציה הראשית"""
    logger.info("=== התחלת הזרקת נתונים למסד הנתונים בענן ===")
    
    # קבלת כתובת מסד הנתונים
    db_url = get_database_url()
    if not db_url:
        logger.error("לא ניתן להמשיך ללא כתובת מסד נתונים")
        return False
    
    try:
        # התחברות למסד הנתונים
        logger.info("מתחבר למסד הנתונים...")
        conn = psycopg2.connect(db_url)
        logger.info("התחברות למסד הנתונים הצליחה")
        
        # יצירת טבלאות
        if not create_tables(conn):
            logger.error("שגיאה ביצירת טבלאות")
            return False
        
        # הוספת נתונים
        if not insert_sample_securities(conn):
            logger.error("שגיאה בהוספת ניירות ערך")
            return False
        
        if not insert_sample_investments(conn):
            logger.error("שגיאה בהוספת השקעות")
            return False
        
        if not insert_sample_user(conn):
            logger.error("שגיאה בהוספת משתמש")
            return False
        
        # בדיקת התוצאה
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM securities")
        securities_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM investments")
        investments_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        logger.info(f"=== סיכום הזרקת נתונים ===")
        logger.info(f"ניירות ערך: {securities_count}")
        logger.info(f"השקעות: {investments_count}")
        logger.info(f"משתמשים: {users_count}")
        
        conn.close()
        logger.info("=== הזרקת נתונים הושלמה בהצלחה ===")
        return True
        
    except Exception as e:
        logger.error(f"שגיאה כללית: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 