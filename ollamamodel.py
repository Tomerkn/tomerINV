import os
import requests


class AI_Agent:
    """
    מחלקה לחיבור לבינה מלאכותית - תומכת ב-Ollama מקומי או בענן
    """
    
    def __init__(self):
        """אתחול מחלקה לחיבור ל-AI"""
        print("אתחול מחלקה לחיבור ל-AI")
        
        # קביעת כתובת ה-Ollama - מקומי או דרך ngrok
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3')
        
        # בדיקה אם Ollama זמין
        self.is_available = self._check_ollama_availability()
        
    def _check_ollama_availability(self) -> bool:
        """בדיקה אם Ollama זמין"""
        try:
            url = f"{self.ollama_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_advice(self, portfolio_data: dict, risk_profile: str) -> str:
        """
        קבלת ייעוץ השקעות מבינה מלאכותית
        
        Args:
            portfolio_data: נתוני התיק
            risk_profile: פרופיל הסיכון
            
        Returns:
            ייעוץ השקעות בעברית
        """
        
        if not self.is_available:
            return self._get_fallback_advice(portfolio_data, risk_profile)
        
        try:
            # בניית הודעה לבינה המלאכותית
            prompt = self._build_prompt(portfolio_data, risk_profile)
            
            # שליחה ל-Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                fallback = self._get_fallback_advice(portfolio_data, risk_profile)
                return result.get('response', fallback)
            else:
                return self._get_fallback_advice(portfolio_data, risk_profile)
                
        except Exception as e:
            print(f"שגיאה בחיבור ל-Ollama: {e}")
            return self._get_fallback_advice(portfolio_data, risk_profile)
    
    def _build_prompt(self, portfolio_data: dict, risk_profile: str) -> str:
        """בניית הודעה לבינה המלאכותית"""
        
        total_value = sum(asset['value'] for asset in portfolio_data.get('assets', []))
        
        prompt = f"""
אתה יועץ השקעות מקצועי. תן ייעוץ קצר ומעשי בעברית.

נתוני התיק:
- ערך כולל: ₪{total_value:,.0f}
- פרופיל סיכון: {risk_profile}

נכסים בתיק:
"""
        
        for asset in portfolio_data.get('assets', []):
            percentage = (asset['value'] / total_value * 100) if total_value > 0 else 0
            value_str = f"₪{asset['value']:,.0f}"
            pct_str = f"({percentage:.1f}%)"
            prompt += f"- {asset['name']}: {value_str} {pct_str}\n"
        
        prompt += """

תן ייעוץ קצר (2-3 משפטים) בעברית על:
1. האם התיק מאוזן?
2. המלצות לשיפור
3. נקודות לתשומת לב

התשובה צריכה להיות בעברית, מקצועית אבל פשוטה להבנה.
"""
        
        return prompt
    
    def _get_fallback_advice(self, portfolio_data: dict, risk_profile: str) -> str:
        """ייעוץ גיבוי כשאין חיבור ל-Ollama"""
        
        total_value = sum(asset['value'] for asset in portfolio_data.get('assets', []))
        num_assets = len(portfolio_data.get('assets', []))
        
        advice = f"ייעוץ בסיסי לתיק שלך (ערך: ₪{total_value:,.0f}):\n\n"
        
        if num_assets < 3:
            advice += "• כדאי לגוון יותר את התיק - הוסף עוד נכסים\n"
        elif num_assets > 10:
            advice += "• התיק מגוון מדי - שקול לאחד נכסים דומים\n"
        else:
            advice += "• רמת הגיוון בתיק נראית טובה\n"
        
        if risk_profile == "נמוך":
            advice += "• התיק מתאים לפרופיל סיכון נמוך\n"
        elif risk_profile == "גבוה":
            advice += "• התיק מתאים לפרופיל סיכון גבוה\n"
        
        advice += "\n💡 טיפ: בדוק את התיק באופן קבוע ועדכן לפי השינויים בשוק"
        
        return advice 