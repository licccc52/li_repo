FROM python:3.8

RUN mkdir /var/www
# workdirの指定
WORKDIR /var/www

# 依存Pythonライブラリ一覧コピー
COPY requirements.txt ./

# 依存Pythonライブラリインストール
RUN pip install --no-cache-dir -r requirements.txt

#CMD ["uwsgi","--ini","/var/www/uwsgi.ini"]
# wsgiの代わりにasgiプロキシを利用しているため、daphneをプロセスシングサーバーとして配置
# nginx経由でhttp方式叩く
CMD ["daphne","-b","0.0.0.0","-p","3031","--proxy-headers","main.asgi:application"]
# sock方式が推奨　　が、うまく配置できない
#CMD ["daphne","-u","/tmp/daphne.sock","main.asgi:application"]
