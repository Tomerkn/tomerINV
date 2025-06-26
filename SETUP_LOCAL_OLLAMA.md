# הוראות להפעלת Ollama מקומי + אפליקציה בענן

## שלב 1: התקנת Ollama מקומי

### macOS:
```bash
# הורדה והתקנה
curl -fsSL https://ollama.ai/install.sh | sh

# הפעלת השירות
ollama serve
```

### Windows:
1. הורד את Ollama מ: https://ollama.ai/download
2. התקן והפעל את הקובץ
3. פתח Command Prompt והרץ:
```cmd
ollama serve
```

### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

## שלב 2: הורדת מודל

```bash
# הורדת מודל llama3 (קטן יותר)
ollama pull llama3

# או מודל גדול יותר
ollama pull llama3.1:8b
```

## שלב 3: התקנת ngrok

### macOS:
```bash
# עם Homebrew
brew install ngrok

# או הורדה ידנית
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.tgz
tar xvzf ngrok-v3-stable-darwin-amd64.tgz
```

### Windows:
1. הורד מ: https://ngrok.com/download
2. חלץ את הקובץ
3. הוסף לנתיב המערכת

### Linux:
```bash
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
```

## שלב 4: הגדרת ngrok

1. הירשם ב: https://dashboard.ngrok.com/signup
2. קבל authtoken
3. הגדר את הטוקן:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

## שלב 5: הפעלת השירותים

### טרמינל 1 - Ollama:
```bash
ollama serve
```

### טרמינל 2 - ngrok:
```bash
ngrok http 11434
```

**חשוב**: שמור את הכתובת שמופיעה ב-ngrok (לדוגמה: `https://abc123.ngrok.io`)

## שלב 6: הגדרת משתנה סביבה

בשרת הענן (Render/Railway), הוסף משתנה סביבה:
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

### אפליקציה לא מתחברת:
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