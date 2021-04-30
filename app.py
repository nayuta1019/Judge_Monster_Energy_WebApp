from tensorflow.keras.models import model_from_json
from flask import Flask, render_template, request
from flask import send_from_directory, url_for
from werkzeug.utils import secure_filename
import os.path
import json
import numpy as np
from PIL import Image
import io
import base64

ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg'])

app = Flask(__name__)

# limit upload file size : 2MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


categories = []

# jsonデータからラベルの情報を読み取る
label_data = os.path.join('label.json')

with open(label_data, 'r', encoding='utf-8') as f:
    label_data = json.load(f)

for label in label_data:
    categories.append(label['label'])


# 保存したモデルの読み込み
model = model_from_json(open('cnn_model.json').read())
# 保存した重みの読み込み
model.load_weights('cnn_model_weight.hdf5')


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/send', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # 画像の読み込み
        img_file = request.files['img_file']

        filename = secure_filename(img_file.filename)

        root, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render_template('index.html')

        # 画像書き込み用バッファを確保して画像データをそこに書き込む
        buf = io.BytesIO()
        image = Image.open(img_file)
        image.save(buf, 'png')
        img_bytes = buf.getvalue()
        print(type(img_bytes))

        # バイナリから画像に変換
        img_png = Image.open(io.BytesIO(img_bytes))
        print(type(img_png))

        # 画像の前処理
        img = img_png.convert('RGB')
        img = img.resize((224, 224))
        x = np.array(img)
        x = x.astype("float32") / 255
        x = x.reshape((1,) + x.shape)

        # 予測
        prediction = model.predict(x)
        label = np.argmax(prediction, axis=1)
        message = "これは" + categories[label[0]] + "です"

        # バイナリデータをbase64でエンコードし, それをさらにutf-8でデコードしておく
        qr_b64str = base64.b64encode(buf.getvalue()).decode("utf-8")

        # image要素のsrc属性に埋め込めこむために、適切に付帯情報を付与する
        qr_b64data = "data:image/png;base64,{}".format(qr_b64str)
        print(type(qr_b64data))
        return render_template('predict.html', message=message,
                               img=qr_b64data)
    else:
        return render_template('index.html')


@app.route('/uploads/<filename>')
def send_dir(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ブラウザにCSSがキャッシュされるのを防ぐ
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == "__main__":
    app.run()
