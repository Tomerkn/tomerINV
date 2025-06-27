#!/bin/bash

echo "🚀 סקריפט פריסה לענן - מערכת ניהול תיק השקעות"
echo "=================================================="

# בדיקה אם Git מותקן
if ! command -v git &> /dev/null; then
    echo "❌ שגיאה: Git לא מותקן!"
    exit 1
fi

# בדיקה אם יש שינויים שלא נדחפו
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  יש שינויים שלא נדחפו ל-Git"
    echo "האם אתה רוצה לדחוף אותם עכשיו? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git add .
        echo "הכנס הודעה לקומיט:"
        read -r commit_message
        git commit -m "$commit_message"
        git push
    else
        echo "❌ לא ניתן להמשיך בלי לדחוף שינויים"
        exit 1
    fi
fi

echo ""
echo "🌐 פריסה ל-Railway"
echo "=================="
echo ""
echo "📋 הוראות פריסה:"
echo "1. היכנס ל: https://railway.app"
echo "2. התחבר עם GitHub"
echo "3. לחץ על 'New Project'"
echo "4. בחר 'Deploy from GitHub repo'"
echo "5. בחר את הרפוזיטורי שלך"
echo "6. הגדר משתני סביבה:"
echo "   - DATABASE_URL: כתובת PostgreSQL"
echo "   - OLLAMA_URL: כתובת Ollama (אופציונלי)"
echo ""
echo "🔗 קישור ל-Railway: https://railway.app"
echo ""
echo "✅ האפליקציה תיפרוס אוטומטית לאחר בחירת הרפוזיטורי"
echo "✅ Railway יזהה את ה-Dockerfile ויפרוס עם gunicorn"
echo "✅ האפליקציה תהיה זמינה בכתובת שניתנת"
echo ""
echo "📝 הערות חשובות:"
echo "- ודא שיש לך DATABASE_URL תקין"
echo "- האפליקציה דורשת PostgreSQL בלבד"
echo "- Ollama אופציונלי - האפליקציה תעבוד גם בלי"
echo ""
echo "🎉 פריסה מוצלחת! האפליקציה שלך תהיה זמינה בענן" 