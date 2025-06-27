#!/bin/bash

echo "🚀 סקריפט פריסה לענן - מערכת ניהול תיק השקעות"
echo "================================================"

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
echo "🌐 בחר פלטפורמת פריסה:"
echo "1. Railway (מומלץ - חינמי)"
echo "2. Heroku (חינמי עם מגבלות)"
echo "3. Docker Compose (מקומי)"
echo "4. יציאה"

read -r choice

case $choice in
    1)
        echo "🚂 פריסה ל-Railway..."
        echo ""
        echo "הוראות:"
        echo "1. היכנס ל: https://railway.app"
        echo "2. התחבר עם GitHub"
        echo "3. לחץ על 'New Project'"
        echo "4. בחר 'Deploy from GitHub repo'"
        echo "5. בחר את הרפוזיטורי שלך"
        echo "6. הוסף משתנה סביבה DATABASE_URL"
        echo "7. המתן לפריסה..."
        echo ""
        echo "✅ הקוד מוכן לפריסה!"
        ;;
    2)
        echo "🦕 פריסה ל-Heroku..."
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI לא מותקן"
            echo "התקן מ: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        echo "הכנס שם האפליקציה ב-Heroku:"
        read -r app_name
        
        heroku create "$app_name"
        heroku addons:create heroku-postgresql:mini
        heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
        git push heroku main
        
        echo "✅ האפליקציה פרוסה ב: https://$app_name.herokuapp.com"
        ;;
    3)
        echo "🐳 הפעלה מקומית עם Docker..."
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker לא מותקן!"
            exit 1
        fi
        
        docker-compose up --build -d
        echo "✅ האפליקציה רצה ב: http://localhost:4000"
        ;;
    4)
        echo "👋 להתראות!"
        exit 0
        ;;
    *)
        echo "❌ בחירה לא תקינה"
        exit 1
        ;;
esac

echo ""
echo "🔗 קישורים שימושיים:"
echo "- האפליקציה: תינתן לאחר הפריסה"
echo "- מסד נתונים: PostgreSQL בענן"
echo "- לוגים: תלויים בפלטפורמה"
echo ""
echo "📞 תמיכה: בדוק את הלוגים אם יש בעיות" 