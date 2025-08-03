FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 依存ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# Uvicornでアプリを起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]