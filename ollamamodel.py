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
        """אתחול הסוכן והתחברות לשירות Ollama"""
        print("=== התחלת אתחול AI_Agent ===")
        # קבלת כתובת שרת Ollama מהסביבה או שימוש בברירת מחדל
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        print(f"OLLAMA_URL מהסביבה: {self.ollama_url}")
        self.model_name = 'llama3.1:8b'  # שם המודל של הבינה המלאכותית
        print(f"מודל שנבחר: {self.model_name}")
        # בדיקה אם Ollama זמין ופועל
        self.ollama_available = self._check_ollama_availability()
        if not self.ollama_available:
            print("Ollama לא זמין - נשתמש בייעוץ פשוט")
        print(f"אתחול AI - Ollama זמין: {self.ollama_available}")
        print("=== סיום אתחול AI_Agent ===")
    
    def _check_ollama_availability(self):
        """בודק אם שרת Ollama זמין ופועל"""
        try:
            print("🔍 בודק זמינות Ollama...")
            print(f"🌐 מנסה להתחבר ל-Ollama בכתובת: {self.ollama_url}")
            # מנסה להתחבר לשרת Ollama עם timeout של 3 שניות
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            print(f"📡 תגובה מ-Ollama: {response.status_code}")
            if response.status_code == 200:  # אם התגובה תקינה
                print("✅ Ollama זמין ופועל!")
                return True
            else:
                print(f"❌ Ollama הגיב עם קוד שגיאה: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("שגיאת חיבור ל-Ollama: לא ניתן להתחבר")
            return False
        except requests.exceptions.Timeout:
            print("פסק זמן בחיבור ל-Ollama: החיבור איטי מדי")
            return False
        except Exception as e:
            print(f"⚠️ שגיאה כללית בבדיקת Ollama: {str(e)}")
            return False
    
    def get_investment_advice(self, portfolio_data, risk_profile):
        """פה אני מקבל ייעוץ השקעות מהבינה המלאכותית - כמו לדבר עם מומחה"""
        try:
            print(f"📊 get_investment_advice נקרא עם {len(portfolio_data)} ניירות ערך")
            # אם Ollama לא זמין, משתמש בייעוץ פשוט
            if not self.ollama_available:
                print("⚠️ Ollama לא זמין, מחזיר ייעוץ סטטי")
                return self._get_professional_advice_for_portfolio(portfolio_data, risk_profile)
            
            print("📝 יוצר prompt עבור Ollama...")
            # פה אני מכין הודעה מפורטת לבינה המלאכותית
            prompt = self._create_professional_investment_prompt(portfolio_data, risk_profile)
            
            print("📤 שולח ל-Ollama...")
            # פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה
            response = self._send_to_ollama(prompt)
            
            print("✨ מעצב את התשובה...")
            # פה אני מחזיר את הייעוץ בעברית פשוטה
            return self._format_professional_advice(response)
            
        except Exception as e:
            # אם משהו לא עובד, אני מחזיר ייעוץ בסיסי
            print(f"❌ שגיאה בייעוץ השקעות: {str(e)}")
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
        """יוצר prompt מקצועי בסגנון של חברות השקעות מובילות"""
        
        # התחלת הprompt עם הוראות לAI
        prompt = f"""אתה יועץ השקעות מקצועי בחברת השקעות מובילת כמו Vanguard או Fidelity. 
כתב ייעוץ מקצועי, ברור ומעשי בעברית.

👤 פרופיל לקוח:
• סובלנות סיכון: {risk_profile}

💼 תיק השקעות נוכחי:"""
        
        total_value = 0  # משתנה לסיכום ערך כולל
        industries = {}  # מילון לאחסון ענפים
        
        # עבור על כל נייר ערך ובנה את הprompt
        for item in portfolio_data:
            value = item['price'] * item['amount']  # חישוב ערך נייר הערך
            total_value += value  # הוסף לסך הכולל
            industry = item.get('industry', 'לא מוגדר')  # קבל ענף
            
            if industry not in industries:
                industries[industry] = 0  # אתחל אם לא קיים
            industries[industry] += value  # הוסף ערך לענף
            
            # הוסף פירוט נייר הערך לprompt
            prompt += f"""
• {item['name']}: {item['amount']} יח' × ₪{item['price']} = ₪{value:,.0f}
  (תחום: {industry}, סוג: {item.get('security_type', 'מניה')})"""
        
        # סיכום והוראות סופיות לAI
        prompt += f"""

💰 ערך כולל: ₪{total_value:,.0f}

כיועץ מקצועי, ספק ניתוח מובנה ובהיר:

1. הערכת התיק הנוכחי (פיזור, איזון, ריכוז)
2. זיהוי סיכונים עיקריים
3. המלצות ספציפיות לשיפור
4. אסטרטגיה המתאימה לפרופיל הסיכון

⚠️ חשוב מאוד:
- כתב בעברית פשוטה אך מקצועית
- אל תכלול קישורים או לינקים מכל סוג
- אל תכלול תגיות HTML או markdown
- רק טקסט פשוט עם נקודות ברורות
- הימנע מביטויים עמומים - תן המלצות קונקרטיות
- אורך מקסימלי: 800 מילים"""
        
        return prompt
    
    def _ensure_model_available(self):
        """וודא שהמודל זמין, הורד אותו אם צריך"""
        try:
            client = ollama.Client(host=self.ollama_url)  # יצור client
            # בדוק אם המודל כבר קיים בשרת
            models = client.list()  # קבל רשימת מודלים
            model_names = [model['name'] for model in models['models']]  # חלץ שמות
            
            if self.model_name not in model_names:  # אם המודל לא קיים
                print(f"⬇️ מוריד מודל {self.model_name}...")
                client.pull(self.model_name)  # הורד את המודל
                print(f"✅ מודל {self.model_name} הורד בהצלחה!")
            else:
                print(f"✅ מודל {self.model_name} כבר קיים")
            return True
        except Exception as e:
            print(f"❌ שגיאה בהורדת מודל: {str(e)}")
            return False

    def _send_to_ollama(self, prompt):
        """פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה"""
        try:
            print(f"📤 שולח prompt ל-Ollama: {prompt[:150]}...")
            
            # השתמש רק ב-ollama client עם timeout ארוך יותר
            client = ollama.Client(host=self.ollama_url)  # יצור client לOllama
            print("🔗 יוצר חיבור ל-Ollama...")
            
            # שלח את הprompt ל-AI
            response = client.chat(
                model=self.model_name,  # שם המודל
                messages=[
                    {"role": "user", "content": prompt}  # ההודעה למודל
                ],
                options={
                    "temperature": 0.7,  # רמת יצירתיות (0-2)
                    "top_p": 0.9,  # גיוון תשובות
                    "num_ctx": 8192  # הקשר רחב יותר - זיכרון ארוך
                }
            )
            
            advice = response['message']['content']  # חלץ את התשובה
            print(f"📥 קיבלתי תשובה מ-Ollama: {len(advice)} תווים")
            
            # בדיקה שהתשובה אמיתית ולא שגיאה
            if len(advice) < 50 or "שגיאה" in advice.lower():
                print("⚠️ תשובה קצרה או עם שגיאה, מחזיר ייעוץ בסיסי")
                return self._get_fallback_advice()
            
            return advice
            
        except Exception as exc:
            print(f"❌ שגיאה ב-Ollama: {exc}")
            return self._get_fallback_advice()
    
    def _get_fallback_advice(self):
        """ייעוץ בסיסי אם יש בעיה עם Ollama"""
        return """📊 ניתוח תיק השקעות

💡 המלצות מקצועיות לתיק שלך:

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

⚠️ זה ייעוץ כללי המבוסס על עקרונות השקעה מוכחים."""
    
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
            emojis_pattern = r'[📊📈📉💡⚠️🚨💰🔍📋🎯✅❌⭐🌟💎🔥🎉🚀📌🎯💼📈📊⚡🔔🔄🎨🎪🏆🌈☀️🌙⭐]'
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
            print("❌ שגיאה בעיצוב הייעוץ")
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

print("=== סיום טעינת ollamamodel.py ===") 