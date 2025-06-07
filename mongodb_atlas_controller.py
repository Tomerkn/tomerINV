"""
מנהל מסד נתונים MongoDB Atlas
תואם לממשק הקיים של portfolio_controller
עומד בעקרונות נורמליזציה עם collections נפרדים
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from pymongo import MongoClient, errors
from bson import ObjectId
import certifi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBAtlasConfig:
    """הגדרות חיבור ל-MongoDB Atlas"""
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "investment_portfolio",
        username: Optional[str] = None,
        password: Optional[str] = None,
        cluster_url: Optional[str] = None
    ):
        self.connection_string = connection_string or self._build_connection_string(
            username or os.getenv('MONGODB_USERNAME'),
            password or os.getenv('MONGODB_PASSWORD'), 
            cluster_url or os.getenv('MONGODB_CLUSTER_URL')
        )
        self.database_name = database_name
        
    def _build_connection_string(self, username: str, password: str, cluster_url: str) -> str:
        """בניית connection string ל-MongoDB Atlas"""
        if not all([username, password, cluster_url]):
            raise ValueError("נדרשים username, password ו-cluster_url למונגו אטלס")
        
        return f"mongodb+srv://{username}:{password}@{cluster_url}/{self.database_name}?retryWrites=true&w=majority"

class MongoDBAtlasManager:
    """מנהל חיבור ל-MongoDB Atlas"""
    
    def __init__(self, config: Optional[MongoDBAtlasConfig] = None):
        self.config = config or MongoDBAtlasConfig()
        self.client = None
        self.db = None
        self._connect()
        
    def _connect(self):
        """התחברות ל-MongoDB Atlas"""
        try:
            # חיבור עם תעודות SSL
            self.client = MongoClient(
                self.config.connection_string,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            
            # בדיקת החיבור
            self.client.admin.command('ping')
            self.db = self.client[self.config.database_name]
            
            logger.info(f"✅ התחברות מוצלחת ל-MongoDB Atlas: {self.config.database_name}")
            
            # יצירת אינדקסים
            self._create_indexes()
            
            # אתחול נתוני ייחוס
            self._populate_reference_data()
            
        except errors.ServerSelectionTimeoutError:
            logger.error("❌ שגיאה: לא ניתן להתחבר ל-MongoDB Atlas - בדוק את פרטי החיבור")
            raise
        except Exception as e:
            logger.error(f"❌ שגיאת חיבור ל-MongoDB Atlas: {e}")
            raise
            
    def _create_indexes(self):
        """יצירת אינדקסים לביצועים טובים"""
        try:
            # אינדקסים לניירות ערך
            self.db.securities.create_index("symbol", unique=True)
            self.db.securities.create_index("name")
            
            # אינדקסים למשתמשים
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)
            
            # אינדקסים לתיקי השקעות
            self.db.portfolios.create_index([("user_id", 1), ("portfolio_name", 1)])
            
            # אינדקסים להחזקות
            self.db.holdings.create_index([("user_id", 1), ("security_id", 1)], unique=True)
            
            # אינדקסים למחירים
            self.db.price_history.create_index([("security_id", 1), ("price_date", -1)])
            
            logger.info("✅ אינדקסים נוצרו בהצלחה")
            
        except Exception as e:
            logger.warning(f"⚠️ שגיאה ביצירת אינדקסים: {e}")
    
    def _populate_reference_data(self):
        """מילוי נתוני ייחוס בסיסיים (collections נפרדים לנורמליזציה)"""
        try:
            # ענפים
            industries_data = [
                {"industry_code": "TECH", "industry_name": "טכנולוגיה", "base_risk_score": 3, "description": "חברות טכנולוגיה"},
                {"industry_code": "BANK", "industry_name": "בנקאות", "base_risk_score": 2, "description": "מוסדות פיננסיים"},
                {"industry_code": "REAL", "industry_name": "נדל\"ן", "base_risk_score": 2, "description": "השקעות נדל\"ן"},
                {"industry_code": "ENERGY", "industry_name": "אנרגיה", "base_risk_score": 4, "description": "חברות אנרגיה"},
                {"industry_code": "HEALTH", "industry_name": "בריאות", "base_risk_score": 2, "description": "תרופות ורפואה"},
                {"industry_code": "CONSUMER", "industry_name": "צריכה", "base_risk_score": 2, "description": "מוצרי צריכה"}
            ]
            
            for industry in industries_data:
                self.db.industries.update_one(
                    {"industry_code": industry["industry_code"]},
                    {"$set": industry},
                    upsert=True
                )
            
            # סוגי ניירות ערך
            security_types_data = [
                {"type_code": "STOCK", "type_name": "מניה", "risk_multiplier": 1.0, "description": "מניה רגילה"},
                {"type_code": "BOND", "type_name": "איגרת חוב", "risk_multiplier": 0.5, "description": "איגרת חוב"},
                {"type_code": "ETF", "type_name": "ETF", "risk_multiplier": 0.8, "description": "קרן נסחרת"},
                {"type_code": "CRYPTO", "type_name": "קריפטו", "risk_multiplier": 2.0, "description": "מטבע דיגיטלי"}
            ]
            
            for sec_type in security_types_data:
                self.db.security_types.update_one(
                    {"type_code": sec_type["type_code"]},
                    {"$set": sec_type},
                    upsert=True
                )
            
            # רמות שונות
            variance_levels_data = [
                {"variance_code": "LOW", "variance_name": "נמוכה", "variance_multiplier": 0.8, "description": "שונות נמוכה"},
                {"variance_code": "MED", "variance_name": "בינונית", "variance_multiplier": 1.0, "description": "שונות בינונית"},
                {"variance_code": "HIGH", "variance_name": "גבוהה", "variance_multiplier": 1.2, "description": "שונות גבוהה"}
            ]
            
            for variance in variance_levels_data:
                self.db.variance_levels.update_one(
                    {"variance_code": variance["variance_code"]},
                    {"$set": variance},
                    upsert=True
                )
            
            logger.info("✅ נתוני ייחוס נוצרו בהצלחה")
            
        except Exception as e:
            logger.warning(f"⚠️ שגיאה במילוי נתוני ייחוס: {e}")

class MongoDBPortfolioController:
    """
    מנהל תיק השקעות עם MongoDB Atlas
    תואם לממשק הקיים של portfolio_controller
    """
    
    def __init__(self, db_manager: MongoDBAtlasManager):
        self.db_manager = db_manager
        self.db = db_manager.db
        
    def get_portfolio(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """
        קבלת תיק השקעות למשתמש
        תואם לממשק הקיים
        """
        try:
            # חיפוש החזקות של המשתמש
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$lookup": {
                    "from": "securities",
                    "localField": "security_id", 
                    "foreignField": "_id",
                    "as": "security_info"
                }},
                {"$unwind": "$security_info"},
                {"$lookup": {
                    "from": "industries",
                    "localField": "security_info.industry_id",
                    "foreignField": "_id", 
                    "as": "industry_info"
                }},
                {"$unwind": "$industry_info"},
                {"$lookup": {
                    "from": "security_types",
                    "localField": "security_info.type_id",
                    "foreignField": "_id",
                    "as": "type_info"
                }},
                {"$unwind": "$type_info"},
                {"$lookup": {
                    "from": "variance_levels", 
                    "localField": "security_info.variance_id",
                    "foreignField": "_id",
                    "as": "variance_info"
                }},
                {"$unwind": "$variance_info"},
                {"$project": {
                    "name": "$security_info.name",
                    "symbol": "$security_info.symbol",
                    "amount": "$quantity",
                    "avg_price": "$avg_purchase_price",
                    "current_price": "$security_info.current_price",
                    "industry": "$industry_info.industry_name",
                    "security_type": "$type_info.type_name", 
                    "variance": "$variance_info.variance_name",
                    "last_updated": "$last_updated"
                }}
            ]
            
            holdings = list(self.db.holdings.aggregate(pipeline))
            
            # חישוב ערכים נוכחיים
            for holding in holdings:
                current_value = holding['amount'] * holding.get('current_price', holding['avg_price'])
                purchase_value = holding['amount'] * holding['avg_price']
                
                holding.update({
                    'current_value': round(current_value, 2),
                    'purchase_value': round(purchase_value, 2),
                    'profit_loss': round(current_value - purchase_value, 2),
                    'profit_loss_percent': round(((current_value - purchase_value) / purchase_value) * 100, 2) if purchase_value > 0 else 0.0
                })
                
                # חישוב סיכון
                holding['risk_level'] = self._calculate_risk_level(
                    holding.get('industry', ''),
                    holding.get('security_type', ''),
                    holding.get('variance', '')
                )
            
            return holdings
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת תיק השקעות: {e}")
            return []
    
    def buy_security(self, name: str, amount: float, industry: str, 
                    variance: str, security_type: str) -> str:
        """
        רכישת נייר ערך
        תואם לממשק הקיים
        """
        try:
            # בדיקה אם נייר הערך קיים
            security = self.db.securities.find_one({"name": name})
            
            if not security:
                # יצירת נייר ערך חדש
                security_id = self._create_security(name, industry, variance, security_type)
            else:
                security_id = security["_id"]
            
            # בדיקה אם יש החזקה קיימת
            existing_holding = self.db.holdings.find_one({
                "user_id": 1,  # משתמש ברירת מחדל
                "security_id": security_id
            })
            
            if existing_holding:
                # עדכון החזקה קיימת
                new_quantity = existing_holding["quantity"] + amount
                new_avg_price = ((existing_holding["quantity"] * existing_holding["avg_purchase_price"]) + 
                               (amount * 100)) / new_quantity  # מחיר ברירת מחדל 100
                
                self.db.holdings.update_one(
                    {"_id": existing_holding["_id"]},
                    {
                        "$set": {
                            "quantity": new_quantity,
                            "avg_purchase_price": new_avg_price,
                            "last_updated": datetime.utcnow()
                        }
                    }
                )
            else:
                # יצירת החזקה חדשה
                holding_data = {
                    "user_id": 1,
                    "security_id": security_id,
                    "quantity": amount,
                    "avg_purchase_price": 100.0,  # מחיר ברירת מחדל
                    "first_purchase_date": datetime.utcnow(),
                    "last_updated": datetime.utcnow()
                }
                self.db.holdings.insert_one(holding_data)
            
            # רישום עסקה
            transaction_data = {
                "user_id": 1,
                "security_id": security_id,
                "transaction_type": "BUY",
                "quantity": amount,
                "price_per_unit": 100.0,
                "total_amount": amount * 100.0,
                "currency": "ILS",
                "transaction_date": datetime.utcnow(),
                "notes": f"רכישה של {name}"
            }
            self.db.transactions.insert_one(transaction_data)
            
            return f"✅ נוסף בהצלחה: {amount} יחידות של {name}"
            
        except Exception as e:
            logger.error(f"❌ שגיאה ברכישת נייר ערך: {e}")
            return f"❌ שגיאה ברכישת {name}: {str(e)}"
    
    def _create_security(self, name: str, industry: str, variance: str, security_type: str) -> ObjectId:
        """יצירת נייר ערך חדש עם קשרים לטבלאות ייחוס"""
        try:
            # חיפוש IDs של נתוני ייחוס
            industry_doc = self.db.industries.find_one({"industry_name": industry})
            type_doc = self.db.security_types.find_one({"type_name": security_type})
            variance_doc = self.db.variance_levels.find_one({"variance_name": variance})
            
            if not all([industry_doc, type_doc, variance_doc]):
                raise ValueError("לא נמצאו נתוני ייחוס מתאימים")
            
            # יצירת נייר ערך
            security_data = {
                "name": name,
                "symbol": name.upper().replace(" ", "")[:10],
                "description": f"נייר ערך בענף {industry}",
                "industry_id": industry_doc["_id"],
                "type_id": type_doc["_id"],
                "variance_id": variance_doc["_id"],
                "current_price": 100.0,  # מחיר ברירת מחדל
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.securities.insert_one(security_data)
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"❌ שגיאה ביצירת נייר ערך: {e}")
            raise
    
    def remove_security(self, name: str) -> str:
        """
        מחיקת נייר ערך מהתיק
        תואם לממשק הקיים
        """
        try:
            # חיפוש נייר הערך
            security = self.db.securities.find_one({"name": name})
            if not security:
                return f"❌ נייר הערך {name} לא נמצא"
            
            # מחיקת החזקה
            result = self.db.holdings.delete_one({
                "user_id": 1,
                "security_id": security["_id"]
            })
            
            if result.deleted_count > 0:
                # רישום עסקת מכירה
                transaction_data = {
                    "user_id": 1,
                    "security_id": security["_id"],
                    "transaction_type": "SELL",
                    "quantity": 0,  # מכירה מלאה
                    "price_per_unit": security.get("current_price", 100.0),
                    "total_amount": 0,
                    "currency": "ILS",
                    "transaction_date": datetime.utcnow(),
                    "notes": f"מכירה מלאה של {name}"
                }
                self.db.transactions.insert_one(transaction_data)
                
                return f"✅ {name} נמחק בהצלחה מהתיק"
            else:
                return f"❌ {name} לא נמצא בתיק"
                
        except Exception as e:
            logger.error(f"❌ שגיאה במחיקת נייר ערך: {e}")
            return f"❌ שגיאה במחיקת {name}: {str(e)}"
    
    def update_security_price(self, name: str, new_price: float) -> str:
        """
        עדכון מחיר נייר ערך
        תואם לממשק הקיים
        """
        try:
            # עדכון המחיר בנייר הערך
            result = self.db.securities.update_one(
                {"name": name},
                {
                    "$set": {
                        "current_price": new_price,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # שמירת היסטוריית מחירים
                security = self.db.securities.find_one({"name": name})
                if security:
                    price_history_data = {
                        "security_id": security["_id"],
                        "price": new_price,
                        "currency": "ILS",
                        "price_date": datetime.utcnow(),
                        "source": "manual_update"
                    }
                    self.db.price_history.insert_one(price_history_data)
                
                return f"✅ מחיר {name} עודכן ל-₪{new_price}"
            else:
                return f"❌ נייר הערך {name} לא נמצא"
                
        except Exception as e:
            logger.error(f"❌ שגיאה בעדכון מחיר: {e}")
            return f"❌ שגיאה בעדכון מחיר {name}: {str(e)}"
    
    def _calculate_risk_level(self, industry: str, security_type: str, variance: str) -> float:
        """חישוב רמת סיכון מבוסס על הפרמטרים"""
        try:
            industry_doc = self.db.industries.find_one({"industry_name": industry})
            type_doc = self.db.security_types.find_one({"type_name": security_type})
            variance_doc = self.db.variance_levels.find_one({"variance_name": variance})
            
            if not all([industry_doc, type_doc, variance_doc]):
                return 0.0
            
            base_risk = industry_doc["base_risk_score"]
            type_mult = type_doc["risk_multiplier"]
            var_mult = variance_doc["variance_multiplier"]
            
            return base_risk * type_mult * var_mult
            
        except Exception as e:
            logger.error(f"❌ שגיאה בחישוב סיכון: {e}")
            return 0.0
    
    def get_total_portfolio_value(self, user_id: int = 1) -> float:
        """חישוב ערך כולל של התיק"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$lookup": {
                    "from": "securities",
                    "localField": "security_id",
                    "foreignField": "_id",
                    "as": "security_info"
                }},
                {"$unwind": "$security_info"},
                {"$group": {
                    "_id": None,
                    "total_value": {
                        "$sum": {
                            "$multiply": [
                                "$quantity",
                                {"$ifNull": ["$security_info.current_price", "$avg_purchase_price"]}
                            ]
                        }
                    }
                }}
            ]
            
            result = list(self.db.holdings.aggregate(pipeline))
            return round(result[0]["total_value"] if result else 0.0, 2)
            
        except Exception as e:
            logger.error(f"❌ שגיאה בחישוב ערך תיק: {e}")
            return 0.0 