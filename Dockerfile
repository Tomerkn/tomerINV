FROM ubuntu:22.04

# התקנת תלויות בסיס
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# התקנת Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# העתקת קבצי האפליקציה
WORKDIR /app
COPY . .

# התקנת Python dependencies
RUN pip3 install -r requirements.txt

# הורדת מודל llama3 (קטן יותר)
RUN ollama pull llama3:8b

# חשיפת פורטים
EXPOSE 11434 4000

# הפעלת Ollama ברקע + האפליקציה
CMD ollama serve & sleep 15 && python3 app.py 