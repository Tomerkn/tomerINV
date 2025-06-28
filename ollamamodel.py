# זה הקובץ שמדבר עם הבינה המלאכותית – כמו יועץ השקעות חכם שמבין הכל
# פה אני שולח מידע על התיק ומקבל ייעוץ חכם בחזרה

import ollama  # פה אני מביא כלי שמאפשר לי לדבר עם שירות Ollama
import os  # כלי לעבודה עם קבצים וסביבה
import requests  # כלי לבדיקת חיבור


class AI_Agent:  # פה אני יוצר סוכן בינה מלאכותית – כמו יועץ השקעות חכם
    """פה אני מדבר עם הבינה המלאכותית ומקבל ייעוץ השקעות חכם"""
    
    def __init__(self):
        """פה אני מתחיל את הסוכן ומתחבר לבינה המלאכותית"""
        print("=== התחלת אתחול AI_Agent ===")
        self.ollama_url = os.environ.get('OLLAMA_URL')
        if not self.ollama_url:
            raise Exception("לא מוגדר OLLAMA_URL! חובה להגדיר את כתובת Ollama בענן במשתני הסביבה.")
        print(f"OLLAMA_URL מהסביבה: {self.ollama_url}")
        self.model_name = 'phi3:mini'
        print(f"מודל שנבחר: {self.model_name}")
        self.ollama_available = self._check_ollama_availability()
        if not self.ollama_available:
            print("Ollama לא זמין - נשתמש בייעוץ פשוט")
        print(f"אתחול מחלקה לחיבור ל-AI - Ollama זמין: {self.ollama_available}")
        print("=== סיום אתחול AI_Agent ===")
    
    def _check_ollama_availability(self):
        """בודק אם שרת Ollama זמין"""
        try:
            print(f"מנסה להתחבר ל-Ollama בכתובת: {self.ollama_url}")
            # מנסה להתחבר לשרת Ollama
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            print(f"תגובה מ-Ollama: {response.status_code}")
            if response.status_code == 200:
                print("Ollama זמין ופועל!")
                return True
            else:
                print(f"Ollama הגיב עם קוד שגיאה: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"שגיאת חיבור ל-Ollama: לא ניתן להתחבר")
            return False
        except requests.exceptions.Timeout as e:
            print(f"פסק זמן בחיבור ל-Ollama: החיבור איטי מדי")
            return False
        except Exception as e:
            print(f"שגיאה כללית בבדיקת Ollama: {str(e)}")
            return False
    
    def get_investment_advice(self, portfolio_data, risk_profile):
        """פה אני מקבל ייעוץ השקעות מהבינה המלאכותית – כמו לדבר עם מומחה"""
        try:
            # אם Ollama לא זמין, משתמש בייעוץ פשוט
            if not self.ollama_available:
                return self._get_simple_advice_for_portfolio(portfolio_data, risk_profile)
            
            # פה אני מכין הודעה מפורטת לבינה המלאכותית
            prompt = self._create_investment_prompt(portfolio_data, risk_profile)
            
            # פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה
            response = self._send_to_ollama(prompt)
            
            # פה אני מחזיר את הייעוץ בעברית פשוטה
            return self._format_advice(response)
            
        except Exception as e:
            # אם משהו לא עובד, אני מחזיר ייעוץ בסיסי
            print(f"שגיאה בייעוץ השקעות: {str(e)}")
            return self._get_simple_advice_for_portfolio(portfolio_data, risk_profile)
    
    def _get_simple_advice_for_portfolio(self, portfolio_data, risk_profile):
        """ייעוץ פשוט כשאין חיבור ל-Ollama"""
        if not portfolio_data:
            return "אין לך עדיין השקעות בתיק. התחל על ידי הוספת מניות או אג\"חים!"
        
        total_value = sum(item['price'] * item['amount'] for item in portfolio_data)
        num_securities = len(portfolio_data)
        most_expensive_stock = max(portfolio_data, key=lambda x: x['price'])['name']
        most_expensive_value = max(portfolio_data, key=lambda x: x['price'])['price']
        cheapest_stock = min(portfolio_data, key=lambda x: x['price'])['name']
        cheapest_value = min(portfolio_data, key=lambda x: x['price'])['price']
        
        advice = f"""
ייעוץ השקעות פשוט (ללא חיבור לבינה מלאכותית):

סיכום התיק שלך:
• ערך כולל: {total_value:.2f} ₪
• מספר ניירות ערך: {num_securities}
• פרופיל סיכון: {risk_profile}
• מניה יקרה ביותר: {most_expensive_stock} ({most_expensive_value:.2f} ₪)
• מניה זולה ביותר: {cheapest_stock} ({cheapest_value:.2f} ₪)

המלצות כלליות:
1. פיזור השקעות - אל תשים את כל הכסף במניה אחת
2. השקעה לטווח ארוך - מניות יכולות לעלות ולרדת בטווח קצר
3. מחקר - קרא על החברות לפני השקעה
4. סבלנות - השקעות טובות לוקחות זמן

סיכונים לשים לב אליהם:
• שינויים במחירים - המניות יכולות לעלות ולרדת
• ריכוזיות - אל תשים יותר מדי כסף במניה אחת
• נזילות - וודא שאתה יכול למכור כשאתה צריך

טיפים נוספים:
• למד על ההשקעות שלך לפני שאתה קונה
• התייעץ עם יועץ השקעות מקצועי
• אל תשקיע כסף שאתה לא יכול להרשות לעצמך להפסיד
• בדוק את הביצועים של המניות שלך באופן קבוע
• שקול להוסיף מניות מתחומים שונים לפיזור טוב יותר
• התייעץ עם יועץ השקעות מקצועי לקבלת ייעוץ מותאם אישית

הערה: זה ייעוץ כללי. לפרטים ספציפיים יותר, כדאי להתייעץ עם מומחה.
"""
        return advice
    
    def _create_investment_prompt(self, portfolio_data, risk_profile):
        """פה אני יוצר הודעה מפורטת לבינה המלאכותית עם כל המידע על התיק"""
        
        # פה אני מתחיל את ההודעה
        prompt = f"""
אתה יועץ השקעות מקצועי. אני רוצה ייעוץ על התיק שלי.

פרופיל הסיכון שלי: {risk_profile}

התיק הנוכחי שלי:
"""
        
        # פה אני מוסיף כל מניה/אג"ח שיש לי
        total_value = 0
        for item in portfolio_data:
            value = item['price'] * item['amount']
            total_value += value
            prompt += f"""
- {item['name']}: {item['amount']} יחידות במחיר {item['price']} (ערך: {value:.2f})
  תחום: {item['industry']}
  סוג: {item['security_type']}
"""
        
        prompt += f"""
ערך כולל של התיק: {total_value:.2f}

אנא תן לי ייעוץ מפורט בעברית פשוטה על:
1. האם התיק שלי מאוזן?
2. איזה שינויים כדאי לי לעשות?
3. איזה סיכונים יש לי?
4. המלצות ספציפיות לשיפור התיק

הסבר הכל בשפה פשוטה ועממית, כאילו אתה מסביר לחבר.
"""
        
        return prompt
    
    def _ensure_model_available(self):
        """וודא שהמודל זמין, הורד אותו אם צריך"""
        try:
            client = ollama.Client(host=self.ollama_url)
            # בדוק אם המודל כבר קיים
            models = client.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names:
                print(f"מוריד מודל {self.model_name}...")
                client.pull(self.model_name)
                print(f"מודל {self.model_name} הורד בהצלחה!")
            else:
                print(f"מודל {self.model_name} כבר קיים")
            return True
        except Exception as e:
            print(f"שגיאה בהורדת מודל: {str(e)}")
            return False

    def _send_to_ollama(self, prompt):
        """פה אני שולח את ההודעה לבינה המלאכותית בענן ומקבל תשובה"""
        try:
            url = f"{self.ollama_url}/api/chat"
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            # Ollama בענן מחזיר את התשובה תחת data['message']['content']
            return data["message"]["content"]
        except Exception as exc:
            raise Exception(f"בעיה בחיבור לבינה המלאכותית בענן: {exc}")
    
    def _format_advice(self, raw_advice):
        """פה אני מעצב את הייעוץ בצורה יפה וקריאה"""
        try:
            # פה אני מנסה לעצב את התשובה בצורה יפה
            if len(raw_advice) > 1000:
                # אם התשובה ארוכה מדי, אני מקצר אותה
                return raw_advice[:1000] + "...\n\n(התשובה קוצרה בגלל אורך)"
            else:
                return raw_advice
        except Exception:
            # אם יש בעיה בעיצוב, אני מחזיר את התשובה כמו שהיא
            return raw_advice
    
    def test_connection(self):
        """פה אני בודק אם החיבור לבינה המלאכותית עובד"""
        try:
            client = ollama.Client(host=self.ollama_url)
            # פה אני שולח הודעה פשוטה לבדיקה
            client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': 'תגיד לי שלום בעברית'
        }
                ]
            )
            return "החיבור לבינה המלאכותית עובד!"
        except Exception as e:
            return f"בעיה בחיבור לבינה המלאכותית: {str(e)}"
    
    def get_simple_advice(self):
        """ייעוץ פשוט ללא צורך בנתוני תיק"""
        return """
ייעוץ השקעות כללי:

עקרונות בסיסיים:
1. אל תשקיע יותר ממה שאתה יכול להרשות לעצמך להפסיד
2. פיזור השקעות - אל תשים את כל הכסף במקום אחד
3. השקעה לטווח ארוך - מניות יכולות לעלות ולרדת בטווח קצר
4. מחקר - קרא על החברות לפני השקעה

סוגי השקעות:
• מניות - חלק בחברה, יכולות לעלות ולרדת הרבה
• אג"חים - הלוואה לחברה/מדינה, יותר יציבות
• קרנות נאמנות - השקעה בכמה מניות ביחד

טיפים:
• התחל עם השקעות קטנות
• למד על ההשקעות שלך
• התייעץ עם מומחה
• בדוק את הביצועים באופן קבוע
• אל תפעל מתוך פחד או חמדנות

זכור: השקעות הן לטווח ארוך. סבלנות היא מפתח להצלחה!
"""

    def get_advice(self):
        """פונקציה כללית לקבלת ייעוץ - משתמשת בפונקציה הפשוטה"""
        return self.get_simple_advice()

print("=== סיום טעינת ollamamodel.py ===") 