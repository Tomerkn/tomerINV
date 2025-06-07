import ollama  # ייבוא ספרייה לחיבור לשירות Ollama (בינה מלאכותית מקומית)
import time  # לזמן תגובה

# AI Agent Class
class AI_Agent:  # מחלקה שמנהלת את החיבור לבינה המלאכותית לייעוץ השקעות
    def __init__(self):  # פונקציה שמתחילה את סוכן הבינה המלאכותית
        print("אתחול מחלקה לחיבור ל-AI")  # מדפיס הודעה שהמחלקה התחילה
        self.model_name = "llama3"  # שם המודל של הבינה המלאכותית שנשתמש בו
        self.timeout = 15  # מגביל זמן תגובה ל-15 שניות

    def get_advice(self, question):  # פונקציה לקבלת ייעוץ השקעות מהבינה המלאכותית
        """קבלת ייעוץ השקעות מודל Ollama"""
        start_time = time.time()  # זמן התחלה
        
        try:  # מנסה לבצע את הפעולה
            # פרומפט פשוט וברור שיתן תגובה מהירה
            simple_prompt = f"""
            You are a financial advisor. Give a SHORT investment advice about: {question}
            
            Answer in this exact format (in Hebrew OR English, pick one language only):
            Stock: [company name]
            Status: [Good/Average/Bad] 
            Recommendation: [Buy/Sell/Hold]
            Reason: [one short reason]
            
            Maximum 4 lines. Be decisive and clear.
            """
            
            # שליחת השאלה לollama עם הגבלות
            response = ollama.generate(
                model=self.model_name,
                prompt=simple_prompt.strip(),
                options={
                    "temperature": 0.1,  # מאוד קר - תגובות יותר עובדתיות
                    "top_p": 0.9,  # הגבלת אפשרויות
                    "top_k": 10,  # עוד הגבלה
                    "num_predict": 100,  # מקסימום 100 מילים
                }
            )
            
            # בדיקת זמן תגובה
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                return self.get_fallback_advice(question)
            
            # נקה התגובה מרווחים מיותרים
            advice = response['response'].strip()
            
            # אם התגובה ארוכה מדי, קצץ אותה
            lines = advice.split('\n')
            if len(lines) > 6:
                advice = '\n'.join(lines[:6])
            
            return advice
            
        except Exception as e:  # אם יש שגיאה
            return self.get_fallback_advice(question, str(e))
    
    def get_fallback_advice(self, question, error=None):  # תגובה חלופית מהירה
        """תגובה מהירה כשollama לא עובד"""
        companies = {
            'MSFT': 'Microsoft - חברת טכנולוגיה חזקה',
            'AAPL': 'Apple - מובילה בסמארטפונים', 
            'GOOGL': 'Google - דומיננטית בחיפוש',
            'AMZN': 'Amazon - מלכת המסחר האלקטרוני',
            'TSLA': 'Tesla - פיונירית ברכבים חשמליים',
            'NVDA': 'Nvidia - מובילה בבינה מלאכותית'
        }
        
        # חיפוש של סמל החברה בשאלה
        company_found = None
        for symbol, description in companies.items():
            if symbol.upper() in question.upper():
                company_found = (symbol, description)
                break
        
        if company_found:
            symbol, desc = company_found
            advice = f"""
מניה: {symbol} - {desc}
מצב: טוב (חברה מובילה)
המלצה: החזק לטווח ארוך
סיבה: חברה יציבה עם צמיחה עקבית
"""
        else:
            advice = f"""
מניה: {question}
מצב: לא ידוע
המלצה: בדוק מקורות נוספים
סיבה: צריך מידע נוסף לפני החלטה
"""
        
        if error:
            advice += f"\n(שגיאה טכנית: ollama לא זמין)"
            
        return advice.strip() 