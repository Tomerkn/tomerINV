#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט להזרקת נתונים ב-Railway
מתחבר ל-PostgreSQL בענן ומוסיף נתוני דוגמה
"""

import os
import psycopg2
import logging

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """הפונקציה הראשית"""
    logger.info("=== התחלת הזרקת נתונים ל-Railway ===")
    
    # קבלת כתובת מסד הנתונים מ-Railway
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("לא נמצא DATABASE_URL - בדוק הגדרות Railway")
        return False
    
    try:
        # התחברות למסד הנתונים
        logger.info("מתחבר למסד הנתונים...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        logger.info("התחברות למסד הנתונים הצליחה")
        
        # יצירת טבלאות
        logger.info("יוצר טבלאות...")
        
        # טבלת ניירות ערך
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
        
        # טבלת השקעות
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                shares INTEGER NOT NULL,
                purchase_price DECIMAL(10,2) NOT NULL,
                purchase_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # טבלת משתמשים
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
        
        # הוספת ניירות ערך לדוגמה
        logger.info("מוסיף ניירות ערך...")
        securities = [
            ('AAPL', 'Apple Inc.', 'Technology', 150.25, 2.5, 50000000, 2500000000000, 25.5, 0.6),
            ('MSFT', 'Microsoft Corporation', 'Technology', 320.75, 1.8, 30000000, 2400000000000, 30.2, 0.8),
            ('GOOGL', 'Alphabet Inc.', 'Technology', 2800.50, 3.2, 20000000, 1800000000000, 28.1, 0.0),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 3300.25, -1.2, 25000000, 1600000000000, 45.3, 0.0),
            ('TSLA', 'Tesla Inc.', 'Automotive', 850.75, 5.8, 40000000, 800000000000, 120.5, 0.0),
            ('NVDA', 'NVIDIA Corporation', 'Technology', 450.30, 4.1, 35000000, 1100000000000, 35.2, 0.2),
            ('META', 'Meta Platforms Inc.', 'Technology', 280.90, 2.7, 28000000, 750000000000, 22.8, 0.0),
            ('JNJ', 'Johnson & Johnson', 'Healthcare', 165.40, 1.2, 15000000, 400000000000, 18.3, 2.8),
            ('V', 'Visa Inc.', 'Financial', 240.60, 2.1, 20000000, 500000000000, 32.1, 0.7),
            ('JPM', 'JPMorgan Chase & Co.', 'Financial', 140.80, 1.5, 25000000, 420000000000, 12.8, 2.9)
        ]
        
        for security in securities:
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
        
        # הוספת השקעות לדוגמה
        logger.info("מוסיף השקעות...")
        investments = [
            (1, 'AAPL', 100, 145.50, '2024-01-15'),
            (1, 'MSFT', 50, 300.25, '2024-02-20'),
            (1, 'GOOGL', 25, 2700.00, '2024-03-10'),
            (1, 'TSLA', 30, 800.00, '2024-01-30'),
            (1, 'NVDA', 40, 420.75, '2024-02-15')
        ]
        
        for investment in investments:
            cursor.execute("""
                INSERT INTO investments (user_id, symbol, shares, purchase_price, purchase_date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, investment)
        
        # הוספת משתמש לדוגמה
        logger.info("מוסיף משתמש לדוגמה...")
        cursor.execute("""
            INSERT INTO users (username, password_hash, email)
            VALUES ('demo_user', 'pbkdf2:sha256:600000$demo_hash$password123', 'demo@example.com')
            ON CONFLICT (username) DO NOTHING
        """)
        
        conn.commit()
        
        # בדיקת התוצאה
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
        logger.error(f"שגיאה: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 