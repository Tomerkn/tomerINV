"""
מודל מסד נתונים מתארח בענן עומד בכללי 3NF
תומך בחיבור ל-PostgreSQL, MySQL ו-SQLite
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager

# הגדרת בסיס עבור כל המודלים
Base = declarative_base()

# הגדרת logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    """טבלת משתמשים - 1NF מתקיים"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # קשרים
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Industry(Base):
    """טבלת ענפים - מנורמלת לפי 3NF"""
    __tablename__ = 'industries'
    
    industry_id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(100), unique=True, nullable=False, index=True)
    industry_code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # קשרים
    securities = relationship("Security", back_populates="industry")
    
    def __repr__(self):
        return f"<Industry(name='{self.industry_name}', code='{self.industry_code}')>"

class SecurityType(Base):
    """טבלת סוגי ניירות ערך - מנורמלת לפי 3NF"""
    __tablename__ = 'security_types'
    
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), unique=True, nullable=False, index=True)
    type_code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    risk_multiplier = Column(DECIMAL(5, 2), nullable=False, default=1.0)
    
    # קשרים
    securities = relationship("Security", back_populates="security_type")
    
    def __repr__(self):
        return f"<SecurityType(name='{self.type_name}', code='{self.type_code}')>"

class VarianceLevel(Base):
    """טבלת רמות שונות - מנורמלת לפי 3NF"""
    __tablename__ = 'variance_levels'
    
    variance_id = Column(Integer, primary_key=True, autoincrement=True)
    variance_level = Column(String(20), unique=True, nullable=False, index=True)
    variance_code = Column(String(5), unique=True, nullable=False)
    variance_multiplier = Column(DECIMAL(5, 2), nullable=False)
    description = Column(Text, nullable=True)
    
    # קשרים
    securities = relationship("Security", back_populates="variance_level")
    
    def __repr__(self):
        return f"<VarianceLevel(level='{self.variance_level}', multiplier={self.variance_multiplier})>"

class Security(Base):
    """טבלת ניירות ערך - עומדת בכללי 3NF"""
    __tablename__ = 'securities'
    
    security_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # מפתחות זרים - קשרים לטבלאות מנורמלות
    industry_id = Column(Integer, ForeignKey('industries.industry_id'), nullable=False)
    type_id = Column(Integer, ForeignKey('security_types.type_id'), nullable=False)
    variance_id = Column(Integer, ForeignKey('variance_levels.variance_id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # קשרים
    industry = relationship("Industry", back_populates="securities")
    security_type = relationship("SecurityType", back_populates="securities")
    variance_level = relationship("VarianceLevel", back_populates="securities")
    holdings = relationship("PortfolioHolding", back_populates="security")
    price_history = relationship("PriceHistory", back_populates="security")
    transactions = relationship("Transaction", back_populates="security")
    
    def calculate_risk_level(self) -> float:
        """חישוב רמת סיכון מבוסס על הקשרים המנורמלים"""
        if not all([self.industry_id, self.security_type, self.variance_level]):
            return 0.0
        
        # מחשב סיכון לפי הנוסחה: industry_id * type_risk_multiplier * variance_multiplier
        base_risk = self.industry_id  # כל ענף יש לו מספר זיהוי שמייצג סיכון בסיסי
        type_multiplier = self.security_type.risk_multiplier if self.security_type else 1.0
        variance_multiplier = self.variance_level.variance_multiplier if self.variance_level else 1.0
        
        return float(base_risk * type_multiplier * variance_multiplier)
    
    def __repr__(self):
        return f"<Security(symbol='{self.symbol}', name='{self.name}')>"

class Portfolio(Base):
    """טבלת תיקי השקעות - 3NF"""
    __tablename__ = 'portfolios'
    
    portfolio_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    portfolio_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # קשרים
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(name='{self.portfolio_name}', user_id={self.user_id})>"

class PortfolioHolding(Base):
    """טבלת החזקות בתיק - עומדת בכללי 3NF"""
    __tablename__ = 'portfolio_holdings'
    
    holding_id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.portfolio_id'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False, default=0)
    avg_purchase_price = Column(DECIMAL(15, 4), nullable=False, default=0)
    first_purchase_date = Column(Date, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # קשרים
    portfolio = relationship("Portfolio", back_populates="holdings")
    security = relationship("Security", back_populates="holdings")
    
    def calculate_total_value(self, current_price: Decimal) -> Decimal:
        """חישוב שווי כולל של החזקה"""
        return self.quantity * current_price
    
    def calculate_profit_loss(self, current_price: Decimal) -> Decimal:
        """חישוב רווח/הפסד"""
        return (current_price - self.avg_purchase_price) * self.quantity
    
    def __repr__(self):
        return f"<PortfolioHolding(portfolio_id={self.portfolio_id}, security_id={self.security_id}, quantity={self.quantity})>"

class PriceHistory(Base):
    """טבלת היסטוריית מחירים - 3NF"""
    __tablename__ = 'price_history'
    
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    price = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='ILS')
    price_date = Column(DateTime, nullable=False, index=True)
    source = Column(String(50), nullable=True)
    
    # קשרים
    security = relationship("Security", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory(security_id={self.security_id}, price={self.price}, date={self.price_date})>"

class Transaction(Base):
    """טבלת עסקאות - עומדת בכללי 3NF"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.portfolio_id'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL, DIVIDEND
    quantity = Column(DECIMAL(15, 4), nullable=False)
    price_per_unit = Column(DECIMAL(15, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='ILS')
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # קשרים
    portfolio = relationship("Portfolio", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(type='{self.transaction_type}', security_id={self.security_id}, quantity={self.quantity})>"

class CloudDatabaseManager:
    """מנהל מסד נתונים בענן - תומך בכמה ספקים"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        אתחול מנהל מסד הנתונים
        connection_string: מחרוזת חיבור למסד הנתונים בענן
        """
        self.connection_string = connection_string or self._get_default_connection_string()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _get_default_connection_string(self) -> str:
        """קבלת מחרוזת חיבור ברירת מחדל מהמשתנים הסביבתיים"""
        # ברירת מחדל - SQLite מקומי לפיתוח
        db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if db_type == 'postgresql':
            user = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASSWORD', '')
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'investment_portfolio')
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        elif db_type == 'mysql':
            user = os.getenv('DB_USER', 'root')
            password = os.getenv('DB_PASSWORD', '')
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '3306')
            database = os.getenv('DB_NAME', 'investment_portfolio')
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        
        else:  # SQLite ברירת מחדל
            db_path = os.getenv('DB_PATH', 'investment_portfolio_3nf.db')
            return f"sqlite:///{db_path}"
    
    def _initialize_database(self):
        """אתחול מנוע מסד הנתונים"""
        try:
            self.engine = create_engine(
                self.connection_string,
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
                pool_pre_ping=True
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info(f"חיבור למסד הנתונים בוצע בהצלחה: {self.connection_string.split('@')[0]}@****")
        except Exception as e:
            logger.error(f"שגיאה בחיבור למסד הנתונים: {e}")
            raise
    
    def create_all_tables(self):
        """יצירת כל הטבלאות במסד הנתונים"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("כל הטבלאות נוצרו בהצלחה")
            self._populate_reference_data()
        except Exception as e:
            logger.error(f"שגיאה ביצירת הטבלאות: {e}")
            raise
    
    def _populate_reference_data(self):
        """אכלוס נתוני ייחוס בסיסיים"""
        with self.get_session() as session:
            try:
                # אכלוס ענפים
                if session.query(Industry).count() == 0:
                    industries = [
                        Industry(industry_name="טכנולוגיה", industry_code="TECH", description="חברות טכנולוגיה"),
                        Industry(industry_name="בנקאות", industry_code="BANK", description="מוסדות פיננסיים"),
                        Industry(industry_name="אנרגיה", industry_code="ENERGY", description="חברות אנרגיה"),
                        Industry(industry_name="תקשורת", industry_code="TELECOM", description="חברות תקשורת"),
                        Industry(industry_name="צרכנות", industry_code="CONSUMER", description="מוצרי צריכה"),
                        Industry(industry_name="בריאות", industry_code="HEALTH", description="תחום הבריאות"),
                    ]
                    session.add_all(industries)
                
                # אכלוס סוגי ניירות ערך
                if session.query(SecurityType).count() == 0:
                    security_types = [
                        SecurityType(type_name="מניה רגילה", type_code="STOCK", risk_multiplier=2.0, description="מניה רגילה"),
                        SecurityType(type_name="אגח ממשלתי", type_code="GOVT", risk_multiplier=1.0, description="אגרת חוב ממשלתית"),
                        SecurityType(type_name="אגח קונצרני", type_code="CORP", risk_multiplier=1.5, description="אגרת חוב קונצרנית"),
                        SecurityType(type_name="קרן נאמנות", type_code="FUND", risk_multiplier=1.2, description="קרן נאמנות"),
                    ]
                    session.add_all(security_types)
                
                # אכלוס רמות שונות
                if session.query(VarianceLevel).count() == 0:
                    variance_levels = [
                        VarianceLevel(variance_level="נמוכה", variance_code="LOW", variance_multiplier=0.5, description="שונות נמוכה"),
                        VarianceLevel(variance_level="בינונית", variance_code="MED", variance_multiplier=1.0, description="שונות בינונית"),
                        VarianceLevel(variance_level="גבוהה", variance_code="HIGH", variance_multiplier=2.0, description="שונות גבוהה"),
                    ]
                    session.add_all(variance_levels)
                
                session.commit()
                logger.info("נתוני ייחוס אוכלסו בהצלחה")
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה באכלוס נתוני ייחוס: {e}")
                raise
    
    @contextmanager
    def get_session(self) -> Session:
        """יצירת session עם context manager"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"שגיאה בסשן מסד הנתונים: {e}")
            raise
        finally:
            session.close()
    
    def get_portfolio_with_holdings(self, user_id: int, portfolio_name: str = "תיק ראשי") -> Dict[str, Any]:
        """קבלת תיק השקעות עם כל החזקות - מתאים לכללי 3NF"""
        with self.get_session() as session:
            portfolio = session.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.portfolio_name == portfolio_name
            ).first()
            
            if not portfolio:
                # יצירת תיק ברירת מחדל
                portfolio = Portfolio(user_id=user_id, portfolio_name=portfolio_name)
                session.add(portfolio)
                session.commit()
                session.refresh(portfolio)
            
            holdings_data = []
            total_value = Decimal('0')
            
            for holding in portfolio.holdings:
                # קבלת מחיר נוכחי מהיסטוריית המחירים
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.security_id == holding.security_id
                ).order_by(PriceHistory.price_date.desc()).first()
                
                current_price = latest_price.price if latest_price else holding.avg_purchase_price
                current_value = holding.calculate_total_value(current_price)
                total_value += current_value
                
                # חישוב רמת סיכון מהמודל המנורמל
                risk_level = holding.security.calculate_risk_level()
                
                holdings_data.append({
                    'name': holding.security.symbol,
                    'price': float(current_price),
                    'amount': float(holding.quantity),
                    'total_value': float(current_value),
                    'risk_level': risk_level,
                    'industry': holding.security.industry.industry_name,
                    'security_type': holding.security.security_type.type_name,
                    'variance_level': holding.security.variance_level.variance_level,
                })
            
            return {
                'portfolio_id': portfolio.portfolio_id,
                'portfolio_name': portfolio.portfolio_name,
                'holdings': holdings_data,
                'total_value': float(total_value),
                'holdings_count': len(holdings_data)
            }
    
    def add_security_to_portfolio(self, user_id: int, symbol: str, quantity: float, 
                                purchase_price: float, industry_name: str, 
                                security_type_name: str, variance_level_name: str) -> bool:
        """הוספת נייר ערך לתיק - מודל מנורמל"""
        with self.get_session() as session:
            try:
                # חיפוש או יצירת נייר ערך
                security = session.query(Security).filter(Security.symbol == symbol).first()
                
                if not security:
                    # קבלת IDs של נתוני ייחוס
                    industry = session.query(Industry).filter(Industry.industry_name == industry_name).first()
                    sec_type = session.query(SecurityType).filter(SecurityType.type_name == security_type_name).first()
                    variance = session.query(VarianceLevel).filter(VarianceLevel.variance_level == variance_level_name).first()
                    
                    if not all([industry, sec_type, variance]):
                        logger.error("נתוני ייחוס חסרים")
                        return False
                    
                    security = Security(
                        symbol=symbol,
                        name=symbol,  # בהעדר שם מלא, נשתמש בסמל
                        industry_id=industry.industry_id,
                        type_id=sec_type.type_id,
                        variance_id=variance.variance_id
                    )
                    session.add(security)
                    session.flush()
                
                # קבלת תיק המשתמש
                portfolio = session.query(Portfolio).filter(
                    Portfolio.user_id == user_id,
                    Portfolio.portfolio_name == "תיק ראשי"
                ).first()
                
                if not portfolio:
                    portfolio = Portfolio(user_id=user_id, portfolio_name="תיק ראשי")
                    session.add(portfolio)
                    session.flush()
                
                # הוספה או עדכון החזקה
                holding = session.query(PortfolioHolding).filter(
                    PortfolioHolding.portfolio_id == portfolio.portfolio_id,
                    PortfolioHolding.security_id == security.security_id
                ).first()
                
                if holding:
                    # עדכון כמות ומחיר ממוצע
                    total_investment = (holding.quantity * holding.avg_purchase_price) + (Decimal(str(quantity)) * Decimal(str(purchase_price)))
                    new_quantity = holding.quantity + Decimal(str(quantity))
                    holding.avg_purchase_price = total_investment / new_quantity
                    holding.quantity = new_quantity
                    holding.last_updated = datetime.utcnow()
                else:
                    # יצירת החזקה חדשה
                    holding = PortfolioHolding(
                        portfolio_id=portfolio.portfolio_id,
                        security_id=security.security_id,
                        quantity=Decimal(str(quantity)),
                        avg_purchase_price=Decimal(str(purchase_price)),
                        first_purchase_date=date.today()
                    )
                    session.add(holding)
                
                # רישום עסקה
                transaction = Transaction(
                    portfolio_id=portfolio.portfolio_id,
                    security_id=security.security_id,
                    transaction_type='BUY',
                    quantity=Decimal(str(quantity)),
                    price_per_unit=Decimal(str(purchase_price)),
                    total_amount=Decimal(str(quantity)) * Decimal(str(purchase_price))
                )
                session.add(transaction)
                
                # עדכון היסטוריית מחירים
                price_history = PriceHistory(
                    security_id=security.security_id,
                    price=Decimal(str(purchase_price)),
                    price_date=datetime.utcnow(),
                    source='MANUAL'
                )
                session.add(price_history)
                
                session.commit()
                logger.info(f"נייר ערך {symbol} נוסף בהצלחה לתיק")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה בהוספת נייר ערך: {e}")
                return False
    
    def remove_security_from_portfolio(self, user_id: int, symbol: str) -> bool:
        """הסרת נייר ערך מהתיק"""
        with self.get_session() as session:
            try:
                # קבלת החזקה
                holding = session.query(PortfolioHolding).join(Portfolio).join(Security).filter(
                    Portfolio.user_id == user_id,
                    Security.symbol == symbol
                ).first()
                
                if not holding:
                    logger.warning(f"נייר ערך {symbol} לא נמצא בתיק")
                    return False
                
                # רישום עסקת מכירה
                transaction = Transaction(
                    portfolio_id=holding.portfolio_id,
                    security_id=holding.security_id,
                    transaction_type='SELL',
                    quantity=holding.quantity,
                    price_per_unit=holding.avg_purchase_price,
                    total_amount=holding.quantity * holding.avg_purchase_price
                )
                session.add(transaction)
                
                # מחיקת החזקה
                session.delete(holding)
                session.commit()
                
                logger.info(f"נייר ערך {symbol} הוסר בהצלחה מהתיק")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה בהסרת נייר ערך: {e}")
                return False 