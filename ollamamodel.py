# זה הקובץ שמדבר עם הבינה המלאכותית – כמו יועץ השקעות חכם שמבין הכל
# פה אני שולח מידע על התיק ומקבל ייעוץ חכם בחזרה

import ollama  # פה אני מביא כלי שמאפשר לי לדבר עם שירות Ollama
import os  # כלי לעבודה עם קבצים וסביבה


class AI_Agent:  # פה אני יוצר סוכן בינה מלאכותית – כמו יועץ השקעות חכם
    """פה אני מדבר עם הבינה המלאכותית ומקבל ייעוץ השקעות חכם"""
    
    def __init__(self):
        """פה אני מתחיל את הסוכן ומתחבר לבינה המלאכותית"""
        # כתובת של Ollama
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        # איזה מודל להשתמש בו (llama2 זה מודל טוב)
        self.model_name = 'llama2'
        print("אתחול מחלקה לחיבור ל-AI")
    
    def get_investment_advice(self, portfolio_data, risk_profile):
        """פה אני מקבל ייעוץ השקעות מהבינה המלאכותית – כמו לדבר עם מומחה"""
        try:
            # פה אני מכין הודעה מפורטת לבינה המלאכותית
            prompt = self._create_investment_prompt(portfolio_data, risk_profile)
            
            # פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה
            response = self._send_to_ollama(prompt)
            
            # פה אני מחזיר את הייעוץ בעברית פשוטה
            return self._format_advice(response)
            
        except Exception as e:
            # אם משהו לא עובד, אני מחזיר ייעוץ בסיסי
            return f"לא הצלחתי לקבל ייעוץ מהבינה המלאכותית: {str(e)}. כדאי לבדוק את החיבור."
    
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
    
    def _send_to_ollama(self, prompt):
        """פה אני שולח את ההודעה לבינה המלאכותית ומקבל תשובה"""
        try:
            # פה אני מתחבר ל-Ollama ושולח את ההודעה
            client = ollama.Client(host=self.ollama_url)
            response = client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            # פה אני מחזיר את התשובה
            return response['message']['content']
            
        except Exception as e:
            # אם יש בעיה עם החיבור, אני מחזיר הודעת שגיאה
            raise Exception(f"בעיה בחיבור לבינה המלאכותית: {str(e)}")
    
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
            return f"בעיה בחיבור: {str(e)}"
    
    def get_simple_advice(self):
        """פה אני מקבל ייעוץ פשוט בלי לנתח תיק ספציפי"""
        try:
            prompt = """
אתה יועץ השקעות. תן לי 3 טיפים פשוטים להשקעות בטוחות בעברית.
הסבר הכל בשפה פשוטה ועממית.
"""
            response = self._send_to_ollama(prompt)
            return self._format_advice(response)
        except Exception:
            return "לא הצלחתי לקבל ייעוץ פשוט מהבינה המלאכותית." 