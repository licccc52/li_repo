# LangridChat
This is a multilingual online chat system demo


## クイックスタート
### Docker
```shell
docker-compose up
```
 
フロントエンド: http://localhost:51471

バックエンド: http://localhost:51472

Redisサーバ: localhost:51479

### ローカル環境構築
```shell
git clone git@github.com:si-ritsumei/LangridChat.git

```
以下の[設定](https://github.com/si-ritsumei/LangridChat#設定)の従って，必要のファイルを作成

```shell
cd ~/LangridChat/LangridChatUI
yarn
#  フロントエンドを起動
yarn run start
```
別のターミナルで以下のコマンドを実行
```shell
cd ~/LangridChat/LangridChat
＃依頼をインストール
pip install -r requirements.txt 

# 初回起動時に以下の二行のコマンドを実行
python manage.py migrate  
python manage.py makemigrations

# 設定を参照して設定ファイルを配置してください

# バックエンドを実行
python manage.py runserver --settings=main.settings.local
```

別のターミナルで以下のコマンドを実行
```shell
# DBを起動
redis-server
```
フロントエンド: http://localhost:3000

バックエンド: http://localhost:8000

## 設定
言語グリッドを介して、多言語翻訳を行います。
そのため、言語グリットに関する設定が必要になります。

`LangridChat/LangridChat/langrid/`の下にファイル`settings.py`を作成して、
```python
_config = {
    'baseUrl': 'https://langrid.org/service_manager/wsdl/kyoto1.langrid:',
    'id': 'YourID',
    'password': 'YourPassword'
}
```
を記入します。

## よく使うコマンド

```shell
# モデルからDBを作成
python manage.py migrate  
docker exec -it langrid_chat python ./manage.py migrate  

# モデルの変更をDBに反映
python ./manage.py makemigrations app_name
docker exec -it langrid_chat python ./manage.py makemigrations app_name

# 管理者アカウントを作成
python manage.py createsuperuser
docker exec -it langrid_chat python manage.py createsuperuser
```
#li_repo
