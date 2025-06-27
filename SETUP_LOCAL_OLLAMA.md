# איך להתקין ולהפעיל Ollama מקומי

זה מדריך פשוט איך להתקין את Ollama (המחשב החכם) על המחשב שלך כדי שהאפליקציה תוכל לתת לך ייעוץ.

## מה זה Ollama?

Ollama זה שירות שמאפשר לך להריץ בינה מלאכותית על המחשב שלך. זה כמו ChatGPT אבל רץ מקומי על המחשב שלך.

## שלב 1: התקנת Ollama

### במחשב Mac:
```bash
# הורדה והתקנה
curl -fsSL https://ollama.ai/install.sh | sh

# הפעלת השירות
ollama serve
```

### במחשב Windows:
1. תוריד את Ollama מהאתר: https://ollama.ai/download
2. תתקין את הקובץ
3. תפתח Command Prompt ותריץ:
```cmd
ollama serve
```

### במחשב Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

## שלב 2: הורדת מודל

אחרי שהשירות רץ, תוריד מודל:

```bash
# הורדת מודל קטן (מהיר יותר)
ollama pull llama3

# או מודל גדול יותר (איטי יותר אבל חכם יותר)
ollama pull llama3.1:8b
```

## שלב 3: התקנת ngrok

ngrok זה כלי שמאפשר לאנשים אחרים באינטרנט לגשת לשירות שרץ על המחשב שלך.

### במחשב Mac:
```bash
# עם Homebrew
brew install ngrok

# או הורדה ידנית
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.tgz
tar xvzf ngrok-v3-stable-darwin-amd64.tgz
```

### במחשב Windows:
1. תוריד מ: https://ngrok.com/download
2. תחלץ את הקובץ
3. תוסיף לנתיב המערכת

### במחשב Linux:
```bash
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
```

## שלב 4: הגדרת ngrok

1. תירשם ב: https://dashboard.ngrok.com/signup
2. תקבל authtoken
3. תגדיר את הטוקן:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

## שלב 5: הפעלת השירותים

### טרמינל ראשון - Ollama:
```bash
ollama serve
```

### טרמינל שני - ngrok:
```bash
ngrok http 11434
```

**חשוב**: תזכור את הכתובת שמופיעה ב-ngrok (לדוגמה: `https://abc123.ngrok.io`)

## שלב 6: הגדרת משתנה סביבה

בשרת הענן (Render/Railway), תוסיף משתנה סביבה:
```
OLLAMA_URL=https://YOUR_NGROK_URL.ngrok.io
```

## שלב 7: בדיקה

1. בדוק ש-Ollama עובד:
```bash
curl http://localhost:11434/api/tags
```

2. בדוק ש-ngrok עובד:
```bash
curl https://YOUR_NGROK_URL.ngrok.io/api/tags
```

## פתרון בעיות

### Ollama לא עובד:
```bash
# בדוק שהשירות רץ
ps aux | grep ollama

# הפעל מחדש
pkill ollama
ollama serve
```

### ngrok לא עובד:
```bash
# בדוק את הטוקן
ngrok config check

# בדוק את החיבור
ngrok http 11434 --log=stdout
```

### האפליקציה לא מתחברת:
1. וודא ש-Ollama רץ על פורט 11434
2. וודא ש-ngrok חשוף לפורט הנכון
3. בדוק את משתנה הסביבה `OLLAMA_URL`

## הערות חשובות

- **אבטחה**: ngrok חושף את המחשב שלך לאינטרנט. השתמש רק לבדיקות
- **ביצועים**: המודל רץ על המחשב שלך, אז הביצועים תלויים בחומרה
- **זיכרון**: llama3 דורש לפחות 4GB RAM
- **אינטרנט**: צריך חיבור יציב לאינטרנט

## גיבוי

אם Ollama לא עובד, האפליקציה תציג ייעוץ בסיסי אוטומטי.

## איך זה עובד?

1. האפליקציה שולחת שאלה ל-Ollama
2. Ollama מעבד את השאלה עם המודל
3. Ollama מחזיר תשובה חכמה
4. האפליקציה מציגה את התשובה למשתמש

## דרישות מערכת

- לפחות 4GB RAM
- חיבור אינטרנט יציב
- מקום פנוי בדיסק (2-4GB למודל)
- מערכת הפעלה מודרנית

## טיפים

- הפעל את Ollama רק כשאתה צריך ייעוץ
- השתמש במודל קטן יותר אם המחשב שלך איטי
- סגור את ngrok כשאתה לא משתמש באפליקציה
- גבה את הנתונים שלך לפני שינויים גדולים 