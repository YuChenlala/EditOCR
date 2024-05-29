import PIL
from flask import Flask, request, jsonify, abort, send_file
import os
from model.OCR import image_to_text
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json
import time
import PIL
from pdf2image import convert_from_path
import random
import uuid
from queue import Queue
from threading import Thread
import pdfkit
import io
from io import BytesIO
import imgkit
from weasyprint import HTML
app = Flask(__name__)
#消息队列
image_queue = Queue()
results = {}  # 用字典保存每张图片的识别结果
CORS(app)
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "ZHOUYANG666"
DATABASE = "ocr_data"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

db = SQLAlchemy(app)

def get_image_binary_data(image_path):
    with open(image_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_data = db.Column(db.LargeBinary(length=2**32-1))
    texts = db.relationship("Text", back_populates="origin_image")

class Text(db.Model):
    __tablename__ = "text"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_data = db.Column(db.JSON)
    origin_image_id = db.Column(db.Integer, db.ForeignKey("image.id"))
    origin_image = db.relationship("Image", back_populates="texts")

with app.app_context():
    db.create_all()

with app.app_context():
    db.create_all()


#限制文件格式为图�?
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg'}

ALLOWED_EXTENSIONS_JSON = {'json'}

def allowed_file_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE


def allowed_file_json(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_JSON

#对传入数�?进�?��?��?
@app.before_request
def validate_files():
    endpoint = request.endpoint
    if endpoint == 'upload':
        if 'image' not in request.files:
            return jsonify({'error': 'Both image and json files are required.'}), 400

        image_file = request.files['image']
        if not allowed_file_image(image_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed extensions are: png, jpg, jpeg.'}), 400

    elif endpoint == 'submit':
        if 'image' not in request.files or 'json' not in request.files:
            return jsonify({'error': 'Both image and json files are required.'}), 400

        image_file = request.files['image']
        json_file = request.files['json']
        if allowed_file_image(image_file.filename):
            print("1")
        if not allowed_file_image(image_file.filename):
            abort(400, {'error': 'Invalid JSON data. Required fields are missing.'})
        if not allowed_file_json(json_file.filename):
            abort(400, {'error': 'Invalid JSON file type. Allowed extensions are: json.'})
        pass

@app.route('/upload', methods = ['POST'])
def UploadApi():
    images = request.files.getlist("image")  # 获取上传的�?�张图片
    # 对图片进行�?�理
    save_folder = 'uploads'
    os.makedirs(save_folder, exist_ok=True)
    cnt = 0
    text_data = {
        'image_num': len(images),
        'message': 'Image uploaded successfully',
    }
    result_list = []
    print(len(images))
    for image_file in images:
        # 保存图片到指定文件夹
        cnt += 1
        id = int(time.time())
        file_path = os.path.join(save_folder, f'{id}.png')
        image_file.save(file_path) #临时保存
        data = {
            'id': cnt,
        }
        data_text = image_to_text(f"uploads/{id}.png")
        os.remove(file_path)        #删除文件
        data['image_data'] = data_text
        result_list.append(data)
    text_data['OCR_data'] = result_list
    # 返回JSON响应
    return jsonify(text_data)

# @app.route('/one-image', methods = ['POST'])
# def OneImageApi():
#     if 'image' not in request.files:
#         return 'No file part'
#     image = request.files.get("image")  # 获取上传的�?�张图片
#     id = str(uuid.uuid4())
#     delay_seconds = random.uniform(2, 7)/10
#     time.sleep(delay_seconds)
#     # 对图片进行�?�理
#     save_folder = 'uploads'
#     id = str(uuid.uuid4())+id
#     os.makedirs(save_folder, exist_ok=True)
#     file_path = os.path.join(save_folder, f"{id}.png")
#     image.save(file_path) #临时保存
#     data = image_to_text(f"uploads/{id}.png")
#     # os.remove(file_path)        #删除文件
#     return jsonify(data)

def process_images():
    while True:
        image_id, image = image_queue.get()
        id = str(uuid.uuid4())
        delay_seconds = random.uniform(2, 7) / 10
        time.sleep(delay_seconds)
        # 对图片进行�?�理
        save_folder = 'uploads'
        id = str(uuid.uuid4()) + id
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, f"{id}.png")
        image.save(file_path)  # 临时保存
        data = image_to_text(f"uploads/{id}.png")
        os.remove(file_path)  # 处理完成后删除文�?
        results[image_id] = data  # 将识�?结果保存到字典中
        image_queue.task_done()

@app.route('/one-image', methods=['POST'])
def OneImageApi():
    if 'image' not in request.files:
        return 'No file part'
    image = request.files.get("image")
    id = str(uuid.uuid4())
    image_queue.put((id, image))
    # 等待图片处理完成后返回识�?结果
    while True:
        time.sleep(1)
        if id in results:
            result_data = results.pop(id)
            return jsonify(result_data)

@app.route('/ceshi', methods = ['POST'])
def CeshiApi():
    json_file_path = 'data.json'
    time.sleep(1)
    # 使用send_file函数返回JSON文件
    return send_file(json_file_path, mimetype='application/json')

# @app.route('/convertToPdf', methods = ['post'])
# def htmlToPDF():
#     if 'file' not in request.files:
#         return 'No file part', 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return 'No selected file', 400
#
#     if file and file.filename.endswith('.json'):
#         file_content = file.read().decode('utf-8')
#         data = json.loads(file_content)
#         html_content = data.get('html', '')
#
#         if not html_content:
#             return 'Invalid JSON content', 400
#
#         pdf = pdfkit.from_string(html_content, False)
#
#         return send_file(
#             io.BytesIO(pdf),
#             mimetype='application/pdf',
#             as_attachment=True,
#             attachment_filename='document.pdf'
#         )
#
#     return 'Invalid file type', 400

@app.route('/submit', methods = ['POST'])
def SubmitApi():
    image = request.files['image']
    json_file = request.form['text']
    print(json_file)
    json_data = json.loads(json_file)
    # 对图片进行�?�理
    save_folder = 'uploads'
    os.makedirs(save_folder, exist_ok=True)
    image_id = int(time.time())
    # 保存图片到指定文件夹
    file_path = os.path.join(save_folder, image.filename)
    image.save(file_path)  # 临时保存
    Tupian = PIL.Image.open(file_path)
    Tupian.close()
    width, height = Tupian.size
    binary_data = get_image_binary_data(file_path)
    image = Image(id=image_id, file_data=binary_data)
    db.session.add(image)
    db.session.commit()
    os.remove(file_path)  # 删除文件
    try:
        for index in json_data:
            for point in index[0]:
                point[0] *= width
                point[1] *= height
        text = Text(file_data=json.dumps(json_data))
        image = Image.query.get(image_id)
        text.origin_image_id = image.id
        db.session.add(text)
        db.session.commit()
    except json.JSONDecodeError:
        error_message = {'error': 'Invalid JSON file'}
        return jsonify(error_message), 400
    return jsonify("success")

@app.route('/convertToPdf', methods=['POST'])
def convertToPdf():
    try:
        data = request.get_json()
        html = data.get('html', '')

        if not html:
            return jsonify({'error': 'No HTML provided'}), 400

        # Convert HTML to PDF using WeasyPrint
        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)
        pdf_file.seek(0)

        # Send PDF file as response
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )
    except Exception as e:
        # Log the error and return a JSON response
        app.logger.error(f"Error generating PDF: {e}")
        return jsonify({'error': 'An error occurred while generating the PDF', 'details': str(e)}), 500

@app.route('/convertToImg', methods=['POST'])
def convertToImg():
    try:
        data = request.get_json()
        html = data.get('html', '')

        if not html:
            return jsonify({'error': 'No HTML provided'}), 400

        # Convert HTML to image using imgkit
        img_file = BytesIO()
        imgkit.from_string(html, img_file, config=config, options={'format': 'png'})
        img_file.seek(0)

        # Send image file as response
        return send_file(
            img_file,
            mimetype='image/png',
            as_attachment=True,
            download_name='document.png'
        )
    except Exception as e:
        # Log the error and return a JSON response
        app.logger.error(f"Error generating image: {e}")
        return jsonify({'error': 'An error occurred while generating the image', 'details': str(e)}), 500

def save_images(images):
    image_urls = []

    for index, image in enumerate(images):
        image_path = f"static/page_{index + 1}.png"
        image.save(image_path)
        image_url = f"http://localhost:5000/{image_path}"
        image_urls.append(image_url)

    return image_urls

# �?动�?�理图片的线�?
image_processor_thread = Thread(target=process_images)
image_processor_thread.daemon = True
image_processor_thread.start()


if __name__ == '__main__':
    app.run(debug=True,port=10011)