"""
מסד נתונים מתארח בענן עם מודל 3NF
תומך ב-PostgreSQL, MySQL, SQLite
עומד בכללי נורמליזציה 1NF, 2NF, 3NF
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey, Text, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

Base = declarative_base()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CloudConfig:
    """הגדרות חיבור למסד נתונים בענן"""
    provider: str = 'local'  # aws, gcp, azure, local
    db_type: str = 'postgresql'
    host: str = 'localhost'
    port: int = 5432
    database: str = 'investment_3nf'
    username: str = 'postgres'
    password: str = ''
    ssl_mode: str = 'require'

# ========== טבלאות נתוני ייחוס (3NF) ==========

class Industry(Base):
    """ענפים - טבלת ייחוס מנורמלת"""
    __tablename__ = 'industries'
    
    industry_id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(100), unique=True, nullable=False)
    industry_code = Column(String(10), unique=True, nullable=False)
    base_risk_score = Column(Integer, nullable=False)
    description = Column(Text)
    
    securities = relationship("Security", back_populates="industry")

class SecurityType(Base):
    """סוגי ניירות ערך - טבלת ייחוס מנורמלת"""
    __tablename__ = 'security_types'
    
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), unique=True, nullable=False)
    type_code = Column(String(10), unique=True, nullable=False)
    risk_multiplier = Column(DECIMAL(3, 1), nullable=False)
    description = Column(Text)
    
    securities = relationship("Security", back_populates="security_type")

class VarianceLevel(Base):
    """רמות שונות - טבלת ייחוס מנורמלת"""
    __tablename__ = 'variance_levels'
    
    variance_id = Column(Integer, primary_key=True, autoincrement=True)
    variance_name = Column(String(20), unique=True, nullable=False)
    variance_code = Column(String(5), unique=True, nullable=False)
    variance_multiplier = Column(DECIMAL(3, 1), nullable=False)
    description = Column(Text)
    
    securities = relationship("Security", back_populates="variance_level")

# ========== טבלאות ישויות עיקריות ==========

class User(Base):
    """משתמשים - 1NF"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")

class Security(Base):
    """ניירות ערך - עומד בכללי 3NF"""
    __tablename__ = 'securities'
    
    security_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # מפתחות זרים - קשרים לטבלאות מנורמלות
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
    
    def calculate_risk_level(self) -> float:
        """חישוב רמת סיכון מבוסס על הקשרים המנורמלים"""
        if not all([self.industry, self.security_type, self.variance_level]):
            return 0.0
        
        base_risk = self.industry.base_risk_score
        type_mult = float(self.security_type.risk_multiplier)
        var_mult = float(self.variance_level.variance_multiplier)
        
        return base_risk * type_mult * var_mult

class Portfolio(Base):
    """תיקי השקעות - 3NF"""
    __tablename__ = 'portfolios'
    
    portfolio_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    portfolio_name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioHolding(Base):
    """החזקות בתיק - עומד בכללי 3NF"""
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
    """היסטוריית מחירים - 3NF"""
    __tablename__ = 'price_history'
    
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('securities.security_id'), nullable=False)
    price = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default='ILS')
    price_date = Column(DateTime, nullable=False)
    source = Column(String(50))
    
    security = relationship("Security", back_populates="price_history")

class Transaction(Base):
    """עסקאות - עומד בכללי 3NF"""
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
    notes = Column(Text)
    
    portfolio = relationship("Portfolio", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")

# ========== מנהל מסד נתונים בענן ==========

class CloudDatabaseManager:
    """מנהל מסד נתונים בענן עם תמיכה בכמה ספקי ענן"""
    
    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or self._load_config_from_env()
        self.engine = None
        self.SessionLocal = None
        self._init_connection()
    
    def _load_config_from_env(self) -> CloudConfig:
        """טעינת הגדרות מהמשתנים הסביבתיים"""
        return CloudConfig(
            provider=os.getenv('CLOUD_PROVIDER', 'local'),
            db_type=os.getenv('DB_TYPE', 'postgresql'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'investment_3nf'),
            username=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            ssl_mode=os.getenv('DB_SSL_MODE', 'require')
        )
    
    def _build_connection_string(self) -> str:
        """בניית מחרוזת חיבור לפי ספק הענן"""
        if self.config.provider == 'aws':
            return (f"postgresql://{self.config.username}:{self.config.password}@"
                   f"{self.config.host}:{self.config.port}/{self.config.database}"
                   f"?sslmode={self.config.ssl_mode}")
        elif self.config.provider == 'gcp':
            return (f"postgresql+pg8000://{self.config.username}:{self.config.password}@"
                   f"{self.config.host}/{self.config.database}")
        elif self.config.provider == 'azure':
            return (f"postgresql://{self.config.username}:{self.config.password}@"
                   f"{self.config.host}:{self.config.port}/{self.config.database}"
                   f"?sslmode={self.config.ssl_mode}")
        else:  # local/sqlite
            return f"sqlite:///{self.config.database}.db"
    
    def _init_connection(self):
        """אתחול חיבור למסד הנתונים"""
        try:
            connection_string = self._build_connection_string()
            
            engine_kwargs = {
                'echo': os.getenv('DB_ECHO', 'False').lower() == 'true',
                'pool_pre_ping': True,
                'pool_recycle': 3600,
            }
            
            if self.config.provider != 'local':
                engine_kwargs.update({
                    'pool_size': 5,
                    'max_overflow': 10,
                })
            
            self.engine = create_engine(connection_string, **engine_kwargs)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info(f"חיבור למסד נתונים {self.config.provider} בוצע בהצלחה")
            
        except Exception as e:
            logger.error(f"שגיאה בחיבור למסד הנתונים: {e}")
            raise
    
    def create_database_schema(self):
        """יצירת סכמת מסד הנתונים"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("סכמת מסד הנתונים נוצרה בהצלחה")
            self._populate_reference_data()
            logger.info("נתוני ייחוס אוכלסו בהצלחה")
        except Exception as e:
            logger.error(f"שגיאה ביצירת סכמת מסד הנתונים: {e}")
            raise
    
    def _populate_reference_data(self):
        """אכלוס נתוני ייחוס בסיסיים"""
        with self.get_session() as session:
            try:
                # אכלוס ענפים
                if session.query(Industry).count() == 0:
                    industries = [
                        Industry(industry_name="טכנולוגיה", industry_code="TECH", base_risk_score=6),
                        Industry(industry_name="בנקאות", industry_code="BANK", base_risk_score=3),
                        Industry(industry_name="אנרגיה", industry_code="ENERGY", base_risk_score=4),
                        Industry(industry_name="תקשורת", industry_code="TELECOM", base_risk_score=2),
                        Industry(industry_name="צרכנות", industry_code="CONSUMER", base_risk_score=1),
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
                        VarianceLevel(variance_name="נמוכה", variance_code="LOW", variance_multiplier=Decimal('0.5')),
                        VarianceLevel(variance_name="בינונית", variance_code="MED", variance_multiplier=Decimal('1.0')),
                        VarianceLevel(variance_name="גבוהה", variance_code="HIGH", variance_multiplier=Decimal('1.0')),
                    ]
                    session.add_all(variance_levels)
                
                session.commit()
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה באכלוס נתוני ייחוס: {e}")
                raise
    
    @contextmanager
    def get_session(self):
        """יצירת session עם context manager"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"שגיאה בסשן: {e}")
            raise
        finally:
            session.close()

# ========== קונטרולר תואם למערכת הקיימת ==========

class CloudPortfolioController:
    """קונטרולר תואם למערכת הקיימת אך משתמש במסד נתונים מנורמל 3NF"""
    
    def __init__(self, db_manager: CloudDatabaseManager):
        self.db = db_manager
        self.default_user_id = 1
    
    def get_portfolio(self, user_id: int = None) -> List[Dict[str, Any]]:
        """קבלת תיק השקעות - תואם לממשק הקיים"""
        user_id = user_id or self.default_user_id
        
        with self.db.get_session() as session:
            portfolio = session.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.portfolio_name == "תיק ראשי"
            ).first()
            
            if not portfolio:
                portfolio = Portfolio(
                    user_id=user_id,
                    portfolio_name="תיק ראשי",
                    description="תיק השקעות ראשי"
                )
                session.add(portfolio)
                session.commit()
                session.refresh(portfolio)
            
            holdings_data = []
            
            for holding in portfolio.holdings:
                latest_price = session.query(PriceHistory).filter(
                    PriceHistory.security_id == holding.security_id
                ).order_by(PriceHistory.price_date.desc()).first()
                
                current_price = latest_price.price if latest_price else holding.avg_purchase_price
                
                holdings_data.append({
                    'name': holding.security.symbol,
                    'price': float(current_price),
                    'amount': float(holding.quantity),
                    'risk_level': holding.security.calculate_risk_level(),
                    'industry': holding.security.industry.industry_name,
                    'security_type': holding.security.security_type.type_name,
                    'variance': holding.security.variance_level.variance_name,
                })
            
            return holdings_data
    
    def buy_security(self, name: str, amount: float, industry: str, 
                    variance: str, security_type: str) -> str:
        """הוספת נייר ערך - תואם לממשק הקיים"""
        
        industry_map = {
            "טכנולוגיה": "TECH", "בנקאות": "BANK", "אנרגיה": "ENERGY",
            "תקשורת": "TELECOM", "צרכנות": "CONSUMER"
        }
        
        type_map = {
            "מניה רגילה": "STOCK", "אגח ממשלתי": "GOVT", "אגח קונצרני": "CORP"
        }
        
        variance_map = {
            "נמוכה": "LOW", "בינונית": "MED", "גבוהה": "HIGH"
        }
        
        with self.db.get_session() as session:
            try:
                security = session.query(Security).filter(Security.symbol == name).first()
                
                if not security:
                    industry_obj = session.query(Industry).filter(
                        Industry.industry_code == industry_map.get(industry, "TECH")
                    ).first()
                    
                    type_obj = session.query(SecurityType).filter(
                        SecurityType.type_code == type_map.get(security_type, "STOCK")
                    ).first()
                    
                    variance_obj = session.query(VarianceLevel).filter(
                        VarianceLevel.variance_code == variance_map.get(variance, "MED")
                    ).first()
                    
                    if not all([industry_obj, type_obj, variance_obj]):
                        return "שגיאה: נתוני ייחוס חסרים"
                    
                    security = Security(
                        symbol=name,
                        name=name,
                        industry_id=industry_obj.industry_id,
                        type_id=type_obj.type_id,
                        variance_id=variance_obj.variance_id
                    )
                    session.add(security)
                    session.flush()
                
                portfolio = session.query(Portfolio).filter(
                    Portfolio.user_id == self.default_user_id,
                    Portfolio.portfolio_name == "תיק ראשי"
                ).first()
                
                if not portfolio:
                    portfolio = Portfolio(
                        user_id=self.default_user_id,
                        portfolio_name="תיק ראשי"
                    )
                    session.add(portfolio)
                    session.flush()
                
                holding = session.query(PortfolioHolding).filter(
                    PortfolioHolding.portfolio_id == portfolio.portfolio_id,
                    PortfolioHolding.security_id == security.security_id
                ).first()
                
                default_price = Decimal('100.0')
                
                if holding:
                    total_cost = (holding.quantity * holding.avg_purchase_price) + (Decimal(str(amount)) * default_price)
                    new_quantity = holding.quantity + Decimal(str(amount))
                    holding.avg_purchase_price = total_cost / new_quantity
                    holding.quantity = new_quantity
                else:
                    holding = PortfolioHolding(
                        portfolio_id=portfolio.portfolio_id,
                        security_id=security.security_id,
                        quantity=Decimal(str(amount)),
                        avg_purchase_price=default_price,
                        first_purchase_date=date.today()
                    )
                    session.add(holding)
                
                transaction = Transaction(
                    portfolio_id=portfolio.portfolio_id,
                    security_id=security.security_id,
                    transaction_type='BUY',
                    quantity=Decimal(str(amount)),
                    price_per_unit=default_price,
                    total_amount=Decimal(str(amount)) * default_price
                )
                session.add(transaction)
                
                price_record = PriceHistory(
                    security_id=security.security_id,
                    price=default_price,
                    price_date=datetime.utcnow(),
                    source='MANUAL'
                )
                session.add(price_record)
                
                session.commit()
                return f"הוספת {amount} יחידות של {name} בהצלחה"
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה בהוספת נייר ערך: {e}")
                return f"שגיאה: {str(e)}"
    
    def remove_security(self, name: str) -> str:
        """הסרת נייר ערך מהתיק - תואם לממשק הקיים"""
        with self.db.get_session() as session:
            try:
                holding = session.query(PortfolioHolding).join(
                    Security, PortfolioHolding.security_id == Security.security_id
                ).join(
                    Portfolio, PortfolioHolding.portfolio_id == Portfolio.portfolio_id
                ).filter(
                    Security.symbol == name,
                    Portfolio.user_id == self.default_user_id
                ).first()
                
                if not holding:
                    return f"נייר הערך {name} לא נמצא בתיק"
                
                transaction = Transaction(
                    portfolio_id=holding.portfolio_id,
                    security_id=holding.security_id,
                    transaction_type='SELL',
                    quantity=holding.quantity,
                    price_per_unit=holding.avg_purchase_price,
                    total_amount=holding.quantity * holding.avg_purchase_price
                )
                session.add(transaction)
                
                session.delete(holding)
                session.commit()
                
                return f"נייר הערך {name} הוסר מהתיק בהצלחה"
                
            except Exception as e:
                session.rollback()
                logger.error(f"שגיאה בהסרת נייר ערך: {e}")
                return f"שגיאה: {str(e)}"

# ========== הגדרות ספקי ענן ==========

AWS_CONFIG = CloudConfig(
    provider='aws',
    host='your-db-instance.region.rds.amazonaws.com',
    database='investment_3nf',
    username='postgres',
    password='your-password'
)

GCP_CONFIG = CloudConfig(
    provider='gcp',
    host='project:region:instance',
    database='investment_3nf',
    username='postgres',
    password='your-password'
)

AZURE_CONFIG = CloudConfig(
    provider='azure',
    host='your-server.postgres.database.azure.com',
    database='investment_3nf',
    username='username@your-server',
    password='your-password'
)

LOCAL_CONFIG = CloudConfig(
    provider='local',
    db_type='sqlite',
    database='investment_3nf'
)

if __name__ == "__main__":
    db_manager = CloudDatabaseManager(LOCAL_CONFIG)
    db_manager.create_database_schema()
    
    controller = CloudPortfolioController(db_manager)
    
    print("הוספת נייר ערך לדוגמה...")
    result = controller.buy_security("AAPL", 10, "טכנולוגיה", "גבוהה", "מניה רגילה")
    print(f"תוצאה: {result}")
    
    print("קבלת תיק השקעות...")
    portfolio = controller.get_portfolio()
    for holding in portfolio:
        print(f"נייר ערך: {holding['name']}, כמות: {holding['amount']}, סיכון: {holding['risk_level']}") 