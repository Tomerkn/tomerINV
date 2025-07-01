# -*- coding: utf-8 -*-
"""
קובץ ollamamodel.py - הבינה המלאכותית של המערכת

קובץ זה מדבר עם הבינה המלאכותית Ollama
פה אני שולח מידע על התיק ומקבל ייעוץ חכם בחזרה
"""

# ייבוא הספריות שאני צריך
import ollama  # פה אני מביא כלי שמאפשר לי לדבר עם שירות Ollama
import os  # כלי לעבודה עם קבצים וסביבה
import requests  # כלי לבדיקת חיבור לשרת
import re  # לעבודה עם ביטויים רגולריים - ניקוי טקסט


class AI_Agent:  # סוכן בינה מלאכותית לייעוץ השקעות מקצועי
    """מחלקת הבינה המלאכותית לייעוץ השקעות - מתחברת לשירות Ollama"""
    
    def __init__(self):
        """Initialize AI agent and connect to Ollama service"""
        print("=== Starting AI_Agent initialization ===")
        # Get Ollama server URL from environment or use default
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        print(f"OLLAMA_URL from environment: {self.ollama_url}")
        # Switch to smaller, faster model
        self.model_name = 'llama3.2:3b'  # Smaller model - 3-4x faster
        print(f"Selected model: {self.model_name}")
        
        # Create persistent client that stays in memory
        self.client = None
        self.model_loaded = False  # Flag if model is loaded
        
        # Check if Ollama is available and running
        self.ollama_available = self._check_ollama_availability()
        if not self.ollama_available:
            print("Ollama not available - using simple advice")
        else:
            # Pre-load model to memory
            print("Loading model to memory...")
            self._preload_model()
        
        print(f"AI initialization - Ollama available: {self.ollama_available}")
        print("=== AI_Agent initialization complete ===")
    
    def _preload_model(self):
        """Pre-load model to memory for fast responses"""
        try:
            print(f"Loading model {self.model_name} to memory...")
            self.client = ollama.Client(host=self.ollama_url)
            
            # Ensure model exists
            models = self.client.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names:
                print(f"Downloading model {self.model_name}...")
                self.client.pull(self.model_name)
                print(f"Model {self.model_name} downloaded successfully!")
            
            # Send short question to load model to memory
            print("Warming up model...")
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "hello"}],
                options={"temperature": 0.7, "num_ctx": 4096}
            )
            
            if response and len(response['message']['content']) > 0:
                self.model_loaded = True
                print("Model loaded successfully to memory! "
                      "Responses will be fast now.")
            else:
                print("Model did not load properly")
                
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model_loaded = False
    
    def _check_ollama_availability(self):
        """Check if Ollama server is available and running"""
        try:
            print("Checking Ollama availability...")
            print(f"Trying to connect to Ollama at: {self.ollama_url}")
            # Try to connect to Ollama server with 3 second timeout
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            print(f"Response from Ollama: {response.status_code}")
            if response.status_code == 200:  # If response is OK
                print("Ollama is available and running!")
                return True
            else:
                print(f"Ollama responded with error code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Connection error to Ollama: cannot connect")
            return False
        except requests.exceptions.Timeout:
            print("Timeout connecting to Ollama: connection too slow")
            return False
        except Exception as e:
            print(f"General error checking Ollama: {str(e)}")
            return False
    
    def get_investment_advice(self, portfolio_data, risk_profile):
        """פה אני מקבל ייעוץ השקעות מהבינה המלאכותית - כמו לדבר עם מומחה"""
        try:
            print(f"get_investment_advice נקרא עם {len(portfolio_data)} ניירות ערך")
            # אם Ollama לא זמין, משתמש בייעוץ פשוט
            if not self.ollama_available:
                print("Ollama לא זמין, מחזיר ייעוץ סטטי")
                return self._get_professional_advice_for_portfolio(portfolio_data, risk_profile)
            
            print("יוצר prompt עבור Ollama...")
            # פה אני מכין הודעה מפורטת לבינה המלאכותית
            prompt = self._create_professional_investment_prompt(portfolio_data, risk_profile)
            
            print("שולח ל-Ollama...")
            # פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה
            response = self._send_to_ollama(prompt)
            
            print("מעצב את התשובה...")
            # פה אני מחזיר את הייעוץ בעברית פשוטה
            return self._format_professional_advice(response)
            
        except Exception as e:
            # אם משהו לא עובד, אני מחזיר ייעוץ בסיסי
            print(f"שגיאה בייעוץ השקעות: {str(e)}")
            return self._get_professional_advice_for_portfolio(portfolio_data, risk_profile)
    
    def _get_professional_advice_for_portfolio(self, portfolio_data, risk_profile):
        """ייעוץ מקצועי כשאין חיבור ל-Ollama - בסגנון Vanguard/Fidelity"""
        if not portfolio_data:  # אם אין נתוני תיק
            return """ניתוח תיק השקעות

אין לך עדיין השקעות בתיק. הנה ההמלצות שלנו להתחלה:

השקעה מומלצת לתחילת דרך:
• התחל עם קרן מגוונת או ETF
• השקע סכום קבוע כל חודש
• שמור 3-6 חודשי הוצאות במזומן לפני השקעה

זכור: השקעה מוצלחת מתחילה בתכנון טוב."""
        
        # חישוב נתוני תיק בסיסיים
        total_value = sum(item['price'] * item['amount'] for item in portfolio_data)  # ערך כולל
        num_securities = len(portfolio_data)  # מספר ניירות ערך
        
        # ניתוח תחומי פעילות
        industries = {}  # מילון לאחסון נתוני ענפים
        for item in portfolio_data:
            industry = item.get('industry', 'לא מוגדר')  # קבל ענף או ברירת מחדל
            if industry not in industries:
                industries[industry] = 0  # אתחל אם לא קיים
            industries[industry] += item['price'] * item['amount']  # הוסף ערך
        
        # חישוב ריכוז התיק - האם יש יותר מדי השקעות במקום אחד
        concentration_risk = "נמוך"
        if num_securities < 5:
            concentration_risk = "גבוה"
        elif num_securities < 10:
            concentration_risk = "בינוני"
        
        # בניית הייעוץ המקצועי
        advice = f"""ניתוח תיק השקעות מקצועי

📊 סיכום נוכחי:
• ערך כולל: ₪{total_value:,.0f}
• מספר נכסים: {num_securities}
• סיכון ריכוז: {concentration_risk}

🏭 פיזור לפי תחומים:"""
        
        # הוסף פירוט ענפים
        for industry, value in industries.items():
            percentage = (value / total_value) * 100  # חישוב אחוז
            advice += f"\n• {industry}: {percentage:.1f}%"
        
        advice += f"""

💡 המלצות מקצועיות:

1. גיוון נוסף
   {self._get_diversification_advice(num_securities, industries, total_value)}

2. אסטרטגיית השקעה
   • המשך השקעה קבועה (Dollar Cost Averaging)
   • בחן את התיק כל 3-6 חודשים
   • שמור על תכנית השקעה לטווח ארוך

3. ניהול סיכונים
   • אל תשקיע יותר מ-5-10% בנכס יחיד
   • שקול הוספת אג"ח לאיזון
   • שמור על קרן חירום מחוץ לתיק

⚠️ זכור: זהו ייעוץ כללי. השקעות כרוכות בסיכון ותמיד מומלץ להתייעץ עם יועץ מקצועי."""
        
        return advice
    
    def _get_diversification_advice(self, num_securities, industries, total_value):
        """המלצות לגיוון בהתבסס על הרכב התיק"""
        if num_securities < 5:  # אם יש מעט מניות
            return "מומלץ להוסיף עוד נכסים להפחתת סיכון ריכוז"
        elif len(industries) < 3:  # אם יש מעט ענפים
            return "שקול הוספת חברות מתחומים נוספים"
        else:
            # בדוק אם יש תחום דומיננטי
            max_industry_value = max(industries.values())  # הערך הגבוה ביותר
            if (max_industry_value / total_value) > 0.5:  # אם יותר מ-50%
                return "יש ריכוז יתר בתחום אחד - מומלץ לאזן"
            return "פיזור התיק סביר, המשך עם תכנית השקעה עקבית"
    
    def _create_professional_investment_prompt(self, portfolio_data, risk_profile):
        """יוצר prompt באנגלית עבור בינה מלאכותית"""
        
        # חישוב נתונים בסיסיים
        total_value = sum(item['price'] * item['amount'] for item in portfolio_data)
        num_securities = len(portfolio_data)
        
        # מציאת החזקות הגדולות
        holdings = []
        for item in portfolio_data:
            value = item['price'] * item['amount']
            holdings.append({
                'name': item['name'],
                'value': value,
                'industry': item.get('industry', 'Other')
            })
        
        holdings = sorted(holdings, key=lambda x: x['value'], reverse=True)[:5]
        
        # ספירת ענפים
        industries = {}
        for item in portfolio_data:
            industry = item.get('industry', 'Other')
            industries[industry] = industries.get(industry, 0) + 1
        
        # בניית רשימת החזקות
        holdings_list = []
        for h in holdings:
            holdings_list.append(f"{h['name']} ({h['industry']}) - {h['value']:,.0f} ILS")
        
        # prompt באנגלית מפורט יותר
        prompt = f"""Analyze this investment portfolio and provide recommendations:

PORTFOLIO OVERVIEW:
- Total value: {total_value:,.0f} ILS
- Number of assets: {num_securities}
- Risk tolerance: {risk_profile}

TOP HOLDINGS:
{chr(10).join(['- ' + h for h in holdings_list])}

MAIN SECTORS:
{', '.join([f"{k}: {v} assets" for k, v in list(industries.items())[:3]])}

Please provide:
1. Portfolio analysis (diversification, risk level)
2. Specific recommendations for each major holding
3. Overall portfolio recommendations
4. Suggestions for improvement

Keep response under 300 words, professional tone."""
        
        return prompt
    
    def _ensure_model_available(self):
        """וודא שהמודל זמין, הורד אותו אם צריך"""
        try:
            client = ollama.Client(host=self.ollama_url)  # יצור client
            # בדוק אם המודל כבר קיים בשרת
            models = client.list()  # קבל רשימת מודלים
            model_names = [model['name'] for model in models['models']]  # חלץ שמות
            
            if self.model_name not in model_names:  # אם המודל לא קיים
                print(f"⬇️ Downloading model {self.model_name}...")
                client.pull(self.model_name)  # הורד את המודל
                print(f"✅ Model {self.model_name} downloaded successfully!")
            else:
                print(f"✅ Model {self.model_name} already exists")
            return True
        except Exception as e:
            print(f"❌ Error downloading model: {str(e)}")
            return False

    def _send_to_ollama(self, prompt):
        """פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה"""
        try:
            print(f"שולח prompt ל-Ollama: {prompt[:80]}...")
            
            # השתמש בclient הקבוע שכבר טעון במודל
            if not self.client or not self.model_loaded:
                print("מודל לא טעון, יוצר client חדש...")
                self.client = ollama.Client(host=self.ollama_url)
            else:
                print("משתמש במודל הטעון - תגובה מהירה!")
            
            # שלח את הprompt ל-AI עם פרמטרים מהירים
            response = self.client.chat(
                model=self.model_name,  # שם המודל
                messages=[
                    {"role": "user", "content": prompt}  # ההודעה למודל
                ],
                options={
                    "temperature": 0.3,  # פחות יצירתיות - יותר מהיר
                    "top_p": 0.5,  # פחות גיוון - יותר מהיר
                    "num_ctx": 1024,  # זיכרון קצר יותר - הרבה יותר מהיר
                    "num_predict": 200,  # מגביל את אורך התשובה
                    "stop": ["\n\n\n"]  # עוצר אחרי 3 שורות ריקות
                }
            )
            
            advice = response['message']['content']  # חלץ את התשובה
            print(f"קיבלתי תשובה מ-Ollama: {len(advice)} תווים")
            
            # בדיקה שהתשובה אמיתית ולא שגיאה
            if len(advice) < 20 or "שגיאה" in advice.lower():
                print("תשובה קצרה או עם שגיאה, מחזיר ייעוץ בסיסי")
                return self._get_fallback_advice()
            
            return advice
            
        except Exception as exc:
            print(f"שגיאה ב-Ollama: {exc}")
            return self._get_fallback_advice()
    
    def _get_fallback_advice(self):
        """ייעוץ בסיסי אם יש בעיה עם Ollama"""
        return """ניתוח תיק השקעות

המלצות מקצועיות לתיק שלך:

1. בדיקת פיזור
   התיק שלך מכיל מספר נכסים שונים. זה טוב, אבל כדאי לוודא שיש גיוון מספק בין תחומים שונים.

2. איזון סיכונים
   • רוב התיק במניות טכנולוגיה? שקול הוספת תחומים אחרים
   • שקול הוספת אגרות חוב לאיזון (20-40% מהתיק)
   • בדוק שאף מניה לא מהווה יותר מ-10% מהתיק

3. אסטרטגיה לטווח ארוך
   • המשך השקעה קבועה כל חודש
   • אל תמכור בעת ירידות שוק
   • בחן את התיק כל רבעון

4. המלצות מיידיות
   • עדכן מחירים באופן קבוע
   • שמור רזרבה של 3-6 חודשי הוצאות
   • שקול יעוץ מקצועי לתכנון מס

זה ייעוץ כללי המבוסס על עקרונות השקעה מוכחים."""
    
    def _format_professional_advice(self, raw_advice):
        """מעצב את הייעוץ לטקסט פשוט וקריא - ללא HTML ואמוג'ים וקישורים"""
        try:
            # התחלה עם הטקסט הגולמי
            clean_text = raw_advice
            
            # הסרת קישורים בפורמט markdown [text](url) - זה הבעיה העיקרית!
            clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)
            
            # הסרת קישורים בפורמט אחר
            clean_text = re.sub(r'https?://[^\s]+', '', clean_text)  # קישורי http
            clean_text = re.sub(r'www\.[^\s]+', '', clean_text)  # קישורי www
            
            # הסרת כל האמוג'ים והסימנים
            emojis_pattern = r'[📈💡⚠️🚨💰🔍📋🎯✅❌⭐💎🔥🎉🚀📌🎯💼📈📊⚡🔔🔄🎨🎪🏆🌈☀️🌙⭐]'
            clean_text = re.sub(emojis_pattern, '', clean_text)
            
            # הסרת כל תגיות HTML כולל h6, h5, strong וכו'
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            
            # הסרת כוכביות (**text** -> text)
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)  # **טקסט**
            clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)  # *טקסט*
            
            # ניקוי מספרים מבלבלים כמו <h6>1.</h6>
            clean_text = re.sub(r'<h\d+>\d+\.</h\d+>', '', clean_text)
            clean_text = re.sub(r'\d+\.\s*(\d+\.)', r'\1', clean_text)
            
            # הסרת תווים מיותרים כמו &amp;
            clean_text = re.sub(r'&amp;', '&', clean_text)  # &amp; -> &
            clean_text = re.sub(r'&quot;', '"', clean_text)  # &quot; -> "
            clean_text = re.sub(r'&lt;', '<', clean_text)  # &lt; -> <
            clean_text = re.sub(r'&gt;', '>', clean_text)  # &gt; -> >
            
            # הסרת מספרים בודדים שתקועים במקומות מוזרים
            clean_text = re.sub(r'\s+\d+\s+', ' ', clean_text)
            
            # ניקוי רווחים מיותרים ושורות כפולות - אחרי כל הניקויים
            clean_text = re.sub(r'\s+', ' ', clean_text)  # רווחים כפולים -> רווח יחיד
            clean_text = re.sub(r'\n\s*\n+', '\n\n', clean_text)  # שורות ריקות כפולות
            clean_text = clean_text.strip()  # הסר רווחים מההתחלה והסוף
            
            # אם התשובה קצרה מדי או לא מכילה תוכן משמעותי, תן ייעוץ בסיסי
            if len(clean_text.strip()) < 100 or "שגיאה" in clean_text.lower():
                simple_advice = """📊 סיכום התיק שלך:
                
יש לך תיק מגוון עם מספר השקעות שונות. זה טוב כי זה מפזר סיכון.

💡 המלצות לשיפור:
• המשך לגוון - אל תשים הכל במקום אחד
• שקול להוסיף אגרות חוב לאיזון
• תשקיע בסכומים קבועים כל חודש
• תחשוב לטווח ארוך - 5-10 שנים

⚠️ דברים להימנע מהם:
• אל תמכור בפאניקה כשהשוק יורד
• אל תשקיע כסף שתצטרך בקרוב
• אל תנסה לנחש את השוק

✅ התיק שלך נראה טוב. המשך ככה ותהיה סבלן."""
                return simple_advice
            
            # הגבלת אורך לטקסט קריא
            if len(clean_text) > 800:
                # חתוך בסוף משפט שלם
                truncated = clean_text[:800]  # קח 800 תווים ראשונים
                last_period = truncated.rfind('.')  # מצא נקודה אחרונה
                if last_period > 400:  # אם יש נקודה סבירה
                    clean_text = truncated[:last_period + 1]  # חתוך בנקודה
                else:
                    clean_text = truncated + "..."  # אחרת הוסף נקודות
            
            # הוספת הערת סיום פשוטה
            if "הערה:" not in clean_text:
                clean_text += "\n\n⚠️ זה ייעוץ כללי, לא המלצה אישית."
            
            return clean_text
            
        except Exception:
            # אם יש בעיה, החזר טקסט בסיסי
            print("❌ Error formatting advice")
            return """📊 התיק שלך נראה בסדר. יש לך מספר השקעות שונות, וזה טוב.
            
💡 המלצות:
• המשך לגוון את ההשקעות
• תשקיע בהדרגה ובסכומים קבועים
• תחשוב לטווח ארוך

⚠️ זה ייעוץ כללי בלבד."""
    
    def test_connection(self):
        """פה אני בודק אם החיבור לבינה המלאכותית עובד"""
        try:
            client = ollama.Client(host=self.ollama_url)  # יצור client
            # פה אני שולח הודעה פשוטה לבדיקה
            client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': 'תגיד לי שלום בעברית'  # בקשה פשוטה לבדיקה
                    }
                ]
            )
            return "✅ החיבור לבינה המלאכותית עובד!"
        except Exception as e:
            return f"❌ בעיה בחיבור לבינה המלאכותית: {str(e)}"
    
    def get_simple_advice(self):
        """ייעוץ מקצועי כללי בסגנון חברות השקעות מובילות"""
        return """📊 ייעוץ השקעות מקצועי

💡 עקרונות השקעה מוכחים:

1. התחל מוקדם ושמור על עקביות
   זמן הוא הנכס החשוב ביותר בהשקעה. הכוח של ריבית דריבית עובד טוב יותר ככל שיש יותר זמן.

2. גיוון הוא המפתח
   "אל תשים את כל הביצים בסל אחד" - פזר השקעות בין נכסים, תחומים וגיאוגרפיות שונות.

3. השקע לטווח ארוך
   השוק יכול להיות תנודתי בטווח קצר, אך היסטורית מציג עלייה לטווח ארוך.

4. שמור על משמעת השקעה
   המשך השקעה גם בזמנים קשים. רכישות במחירים נמוכים יכולות לשפר את התשואה.

5. עלויות נמוכות = תשואות גבוהות יותר
   כל שקל ששולם בעמלות הוא שקל פחות שגדל בתיק.

🎯 המלצות מעשיות:
• התחל עם קרן מגוונת או ETF
• השקע סכום קבוע כל חודש
• בחן את התיק אחת לרבעון, לא יומית
• שמור תמיד קרן חירום מחוץ לתיק

⚠️ זכור: השקעה מוצלחת דורשת סבלנות ומשמעת, לא ניחושים על השוק."""

    def get_advice(self, portfolio_data=None):
        """פונקציה כללית לקבלת ייעוץ - משתמשת בפונקציה הפשוטה או מפורטת"""
        if portfolio_data:  # אם יש נתוני תיק
            # נתן ייעוץ מותאם אישית
            return self.get_investment_advice(portfolio_data, "בינוני")
        else:  # אם אין נתוני תיק
            # נתן ייעוץ כללי
            return self.get_simple_advice()

print("=== AI_Agent initialization complete ===") 