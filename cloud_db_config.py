"""
הגדרות חיבור למסד נתונים בענן עם מודל 3NF
תומך ב: PostgreSQL (AWS RDS/Google Cloud SQL), MySQL, SQLite
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

# בסיס לכל המודלים
Base = declarative_base()

@dataclass
class DatabaseConfig:
    """הגדרות מסד נתונים"""
    db_type: str = 'postgresql'  # postgresql, mysql, sqlite
    host: str = 'localhost'
    port: int = 5432
    database: str = 'investment_portfolio_3nf'
    username: str = 'postgres'
    password: str = ''
    ssl_mode: str = 'prefer'
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

# מודלים עומדים בכללי 3NF

class User(Base):
    """משתמשים - 1NF: כל שדה אטומי"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")

class Industry(Base):
    """ענפים - 3NF: הפרדת נתוני ייחוס"""
    __tablename__ = 'industries'
    
    industry_id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(100), unique=True, nullable=False)
    industry_code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    base_risk_factor = Column(DECIMAL(3, 1), nullable=False, default=1.0)
    
    securities = relationship("Security", back_populates="industry")

class SecurityType(Base):
    """סוגי ניירות ערך - 3NF: הפרדת סיווג"""
    __tablename__ = 'security_types'
    
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), unique=True, nullable=False)
    type_code = Column(String(10), unique=True, nullable=False)
    risk_multiplier = Column(DECIMAL(3, 1), nullable=False, default=1.0)
    description = Column(Text, nullable=True)
    
    securities = relationship("Security", back_populates="security_type")

class VarianceLevel(Base):
    """רמות שונות - 3NF: הפרדת מאפייני סיכון"""
    __tablename__ = 'variance_levels'
    
    variance_id = Column(Integer, primary_key=True, autoincrement=True)
    variance_level = Column(String(20), unique=True, nullable=False)
    variance_code = Column(String(5), unique=True, nullable=False)
    variance_multiplier = Column(DECIMAL(3, 1), nullable=False)
    description = Column(Text, nullable=True)
    
    securities = relationship("Security", back_populates="variance_level")

class Security(Base):
    """ניירות ערך - 3NF: תלות רק במפתח ראשי"""
    __tablename__ = 'securities'
    
    security_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # מפתחות זרים - קשרים מנורמלים
    industry_id = Column(Integer, ForeignKey('industries.industry_id'), nullable=False)
    type_id = Column(Integer, ForeignKey('security_types.type_id'), nullable=False)
    variance_id = Column(Integer, ForeignKey('variance_levels.variance_id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # קשרים
    industry = relationship("Industry", back_populates="securities")
    security_type = relationship("SecurityType", back_populates="securities")
    variance_level = relationship("VarianceLevel", back_populates="securities")
    holdings = relationship("PortfolioHolding", back_populates="security")
    price_history = relationship("PriceHistory", back_populates="security")
    transactions = relationship("Transaction", back_populates="security")
    
    def calculate_risk_score(self) -> float:
        """חישוב ציון סיכון מבוסס על הקשרים המנורמלים"""
        if not all([self.industry, self.security_type, self.variance_level]):
            return 0.0
        
        base_risk = float(self.industry.base_risk_factor)
        type_mult = float(self.security_type.risk_multiplier)
        var_mult = float(self.variance_level.variance_multiplier)
        
        return base_risk * type_mult * var_mult

class Portfolio(Base):
    """תיקי השקעות - 3NF"""
    __tablename__ = 'portfolios'
    
    portfolio_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    portfolio_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioHolding(Base):
    """החזקות בתיק - 3NF: הפרדת נתוני החזקה מנתוני נייר ערך"""
    __tablename__ = 'portfolio_holdings'
    
    holding_id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.portfolio_id'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False, default=0)
    avg_purchase_price = Column(DECIMAL(15, 4), nullable=False, default=0)
    first_purchase_date = Column(Date, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="holdings")
    security = relationship("Security", back_populates="holdings")

class PriceHistory(Base):
    """היסטוריית מחירים - 3NF: הפרדת נתוני מחיר מנתוני נייר ערך"""
    __tablename__ = 'price_history'
    
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    price = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='ILS')
    price_date = Column(DateTime, nullable=False, index=True)
    source = Column(String(50), nullable=True)
    
    security = relationship("Security", back_populates="price_history")

class Transaction(Base):
    """עסקאות - 3NF: רישום מלא של כל עסקה"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.portfolio_id'), nullable=False)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL, DIVIDEND
    quantity = Column(DECIMAL(15, 4), nullable=False)
    price_per_unit = Column(DECIMAL(15, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='ILS')
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    portfolio = relationship("Portfolio", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")

class CloudDatabase:
    """מנהל מסד נתונים בענן - 3NF compliant"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or self._load_config_from_env()
        self.engine = None
        self.SessionLocal = None
        self._init_engine()
    
    def _load_config_from_env(self) -> DatabaseConfig:
        """טעינת הגדרות מהמשתנים הסביבתיים"""
        return DatabaseConfig(
            db_type=os.getenv('DB_TYPE', 'postgresql'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'investment_portfolio_3nf'),
            username=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            ssl_mode=os.getenv('DB_SSL_MODE', 'prefer'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
            echo=os.getenv('DB_ECHO', 'False').lower() == 'true'
        )
    
    def _init_engine(self):
        """אתחול מנוע מסד הנתונים"""
        connection_string = self._build_connection_string()
        
        self.engine = create_engine(
            connection_string,
            echo=self.config.echo,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def _build_connection_string(self) -> str:
        """בניית מחרוזת חיבור לפי סוג מסד הנתונים"""
        if self.config.db_type == 'postgresql':
            return (f"postgresql://{self.config.username}:{self.config.password}@"
                   f"{self.config.host}:{self.config.port}/{self.config.database}"
                   f"?sslmode={self.config.ssl_mode}")
        
        elif self.config.db_type == 'mysql':
            return (f"mysql+pymysql://{self.config.username}:{self.config.password}@"
                   f"{self.config.host}:{self.config.port}/{self.config.database}")
        
        else:  # SQLite
            return f"sqlite:///{self.config.database}.db"
    
    def create_all_tables(self):
        """יצירת כל הטבלאות"""
        Base.metadata.create_all(bind=self.engine)
        self._populate_reference_data()
    
    def _populate_reference_data(self):
        """אכלוס נתוני ייחוס - רק אם הטבלאות ריקות"""
        with self.get_session() as session:
            # אכלוס ענפים
            if session.query(Industry).count() == 0:
                industries = [
                    Industry(industry_name="טכנולוגיה", industry_code="TECH", base_risk_factor=Decimal('6.0')),
                    Industry(industry_name="בנקאות", industry_code="BANK", base_risk_factor=Decimal('3.0')),
                    Industry(industry_name="אנרגיה", industry_code="ENERGY", base_risk_factor=Decimal('4.0')),
                    Industry(industry_name="תקשורת", industry_code="TELECOM", base_risk_factor=Decimal('2.0')),
                    Industry(industry_name="צרכנות", industry_code="CONSUMER", base_risk_factor=Decimal('1.0')),
                ]
                session.add_all(industries)
            
            # אכלוס סוגי ניירות ערך
            if session.query(SecurityType).count() == 0:
                security_types = [
                    SecurityType(type_name="מניה רגילה", type_code="STOCK", risk_multiplier=Decimal('2.0')),
                    SecurityType(type_name="אגח ממשלתי", type_code="GOVT", risk_multiplier=Decimal('1.0')),
                    SecurityType(type_name="אגח קונצרני", type_code="CORP", risk_multiplier=Decimal('2.0')),
                ]
                session.add_all(security_types)
            
            # אכלוס רמות שונות
            if session.query(VarianceLevel).count() == 0:
                variance_levels = [
                    VarianceLevel(variance_level="נמוכה", variance_code="LOW", variance_multiplier=Decimal('0.5')),
                    VarianceLevel(variance_level="בינונית", variance_code="MED", variance_multiplier=Decimal('1.0')),
                    VarianceLevel(variance_level="גבוהה", variance_code="HIGH", variance_multiplier=Decimal('1.0')),
                ]
                session.add_all(variance_levels)
            
            session.commit()
    
    @contextmanager
    def get_session(self):
        """יצירת session"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# מחלקת עזר לשימוש במערכת הקיימת
class CloudPortfolioController:
    """קונטרולר תואם למערכת הקיימת אך משתמש במסד נתונים מנורמל"""
    
    def __init__(self, db: CloudDatabase):
        self.db = db
    
    def get_portfolio(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """קבלת תיק השקעות - תואם לממשק הקיים"""
        with self.db.get_session() as session:
            # קבלת תיק ברירת מחדל
            portfolio = session.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.portfolio_name == "תיק ראשי"
            ).first()
            
            if not portfolio:
                return []
            
            holdings_data = []
            for holding in portfolio.holdings:
                # קבלת מחיר אחרון
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.security_id == holding.security_id
                ).order_by(PriceHistory.price_date.desc()).first()
                
                current_price = latest_price.price if latest_price else holding.avg_purchase_price
                
                holdings_data.append({
                    'name': holding.security.symbol,
                    'price': float(current_price),
                    'amount': float(holding.quantity),
                    'risk_level': holding.security.calculate_risk_score(),
                    'industry': holding.security.industry.industry_name,
                    'security_type': holding.security.security_type.type_name,
                    'variance': holding.security.variance_level.variance_level,
                })
            
            return holdings_data
    
    def buy_security(self, name: str, amount: float, industry: str, 
                    variance: str, security_type: str) -> str:
        """הוספת נייר ערך - תואם לממשק הקיים"""
        # מעבר משם לקוד (לפי המיפוי הקיים)
        industry_mapping = {
            "טכנולוגיה": "TECH", "בנקאות": "BANK", "אנרגיה": "ENERGY",
            "תקשורת": "TELECOM", "צרכנות": "CONSUMER"
        }
        
        type_mapping = {
            "מניה רגילה": "STOCK", "אגח ממשלתי": "GOVT", "אגח קונצרני": "CORP"
        }
        
        variance_mapping = {
            "נמוכה": "LOW", "בינונית": "MED", "גבוהה": "HIGH"
        }
        
        with self.db.get_session() as session:
            try:
                # יצירת או עדכון נייר ערך
                security = session.query(Security).filter(Security.symbol == name).first()
                
                if not security:
                    # קבלת IDs של נתוני ייחוס
                    industry_obj = session.query(Industry).filter(
                        Industry.industry_code == industry_mapping.get(industry, "TECH")
                    ).first()
                    
                    type_obj = session.query(SecurityType).filter(
                        SecurityType.type_code == type_mapping.get(security_type, "STOCK")
                    ).first()
                    
                    variance_obj = session.query(VarianceLevel).filter(
                        VarianceLevel.variance_code == variance_mapping.get(variance, "MED")
                    ).first()
                    
                    security = Security(
                        symbol=name,
                        name=name,
                        industry_id=industry_obj.industry_id,
                        type_id=type_obj.type_id,
                        variance_id=variance_obj.variance_id
                    )
                    session.add(security)
                    session.flush()
                
                # קבלת או יצירת תיק
                portfolio = session.query(Portfolio).filter(
                    Portfolio.user_id == 1,  # user_id ברירת מחדל
                    Portfolio.portfolio_name == "תיק ראשי"
                ).first()
                
                if not portfolio:
                    portfolio = Portfolio(user_id=1, portfolio_name="תיק ראשי")
                    session.add(portfolio)
                    session.flush()
                
                # הוספה או עדכון החזקה
                holding = session.query(PortfolioHolding).filter(
                    PortfolioHolding.portfolio_id == portfolio.portfolio_id,
                    PortfolioHolding.security_id == security.security_id
                ).first()
                
                if holding:
                    holding.quantity += Decimal(str(amount))
                else:
                    holding = PortfolioHolding(
                        portfolio_id=portfolio.portfolio_id,
                        security_id=security.security_id,
                        quantity=Decimal(str(amount)),
                        avg_purchase_price=Decimal('100.0'),  # ברירת מחדל
                        first_purchase_date=datetime.now().date()
                    )
                    session.add(holding)
                
                session.commit()
                return f"הוספת {amount} יחידות של {name}"
                
            except Exception as e:
                session.rollback()
                return f"שגיאה: {str(e)}"
    
    def remove_security(self, name: str) -> str:
        """הסרת נייר ערך - תואם לממשק הקיים"""
        with self.db.get_session() as session:
            try:
                holding = session.query(PortfolioHolding).join(Security).filter(
                    Security.symbol == name
                ).first()
                
                if holding:
                    session.delete(holding)
                    session.commit()
                    return f"נייר הערך {name} הוסר מהתיק"
                else:
                    return f"נייר הערך {name} לא נמצא"
                    
            except Exception as e:
                session.rollback()
                return f"שגיאה: {str(e)}"

# הגדרות חיבור לענן
CLOUD_CONFIGS = {
    # AWS RDS PostgreSQL
    'aws_rds': DatabaseConfig(
        db_type='postgresql',
        host='your-instance.region.rds.amazonaws.com',
        port=5432,
        database='investment_portfolio_3nf',
        username='postgres',
        password='your-password',
        ssl_mode='require'
    ),
    
    # Google Cloud SQL PostgreSQL
    'gcp_sql': DatabaseConfig(
        db_type='postgresql',
        host='your-project:region:instance',
        port=5432,
        database='investment_portfolio_3nf',
        username='postgres',
        password='your-password',
        ssl_mode='require'
    ),
    
    # Azure Database for PostgreSQL
    'azure_postgres': DatabaseConfig(
        db_type='postgresql',
        host='your-server.postgres.database.azure.com',
        port=5432,
        database='investment_portfolio_3nf',
        username='username@your-server',
        password='your-password',
        ssl_mode='require'
    ),
    
    # פיתוח מקומי
    'local_dev': DatabaseConfig(
        db_type='sqlite',
        database='investment_portfolio_3nf'
    )
} 