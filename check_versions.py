#!/usr/bin/env python3
"""
בדיקה מהירה של גרסאות Flask ו-Werkzeug
"""

import pkg_resources


def quick_check():
    """בדיקה מהירה של תאימות גרסאות"""
    try:
        flask_v = pkg_resources.get_distribution("Flask").version
        werkzeug_v = pkg_resources.get_distribution("Werkzeug").version
        
        print(f"Flask: {flask_v}")
        print(f"Werkzeug: {werkzeug_v}")
        
        # בדיקת תאימות
        if (flask_v.startswith("2.2") and werkzeug_v.startswith("2.2")):
            print("✅ תואם")
            return True
        elif (flask_v.startswith("2.3") and werkzeug_v.startswith("2.3")):
            print("✅ תואם")
            return True
        else:
            print("❌ לא תואם - הרץ: python fix_versions.py")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False


if __name__ == "__main__":
    quick_check() 