## これは何?
CNNでモンスターエナジーの画像を種類ごとに判別するプログラムをWebアプリにしました  
[サイトに移動][1]

[1]:https://judge-monster-energy-app.herokuapp.com/

## 開発環境
macOS Catalina  
Python : 3.6.9  
tensorflow : 2.4.1  
Flask : 1.1.2

## Setup
```
python -m venv hoge
pip install --upgrade pip
pip install --upgrade tensorflow
pip install Pillow
pip install Flask
pip install gunicorn
```
## gunicornサーバ起動
```
gunicorn -w 1 app:app
```

### メモ
ブラウザにCSSがキャッシュされるのを防ぐためにapp.context_processorで
url_forをoverride

HerokuではUPLOAD_FOLDERを使えなかったため送信された画像を保存するのではなく直接htmlに渡すように

その際request.files[]で受け取ったままではhtmlに渡せないのでbase64でエンコードし, それをさらにutf-8でデコードしhtmlのimage要素のsrc属性に埋め込めこむために, 適切に付帯情報を付与する