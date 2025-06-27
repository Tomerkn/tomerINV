#!/bin/bash

# סקריפט ניקוי מלא
echo "=== ניקוי סביבת Docker ==="
echo "=== תאריך: $(date) ==="

# צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# עצירת שירותים
print_status "עצירת שירותים..."
docker-compose down -v 2>/dev/null || true

# מחיקת קונטיינרים
print_status "מחיקת קונטיינרים..."
docker rm -f $(docker ps -aq) 2>/dev/null || true

# מחיקת תמונות
print_status "מחיקת תמונות..."
docker rmi -f $(docker images -q) 2>/dev/null || true

# ניקוי נפחים
print_status "ניקוי נפחים..."
docker volume prune -f

# ניקוי רשתות
print_status "ניקוי רשתות..."
docker network prune -f

# ניקוי מערכת
print_status "ניקוי מערכת..."
docker system prune -af

print_status "ניקוי הושלם!" 