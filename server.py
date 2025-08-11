from flask import Flask, send_from_directory, jsonify, request, render_template
from flask_cors import CORS
import os, json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
MODEL_MAP_FILE = os.path.join(os.getcwd(), 'model_map.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(MODEL_MAP_FILE):
    with open(MODEL_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, indent=4)

@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/', methods=['POST'])
def upload_model():
    marker = request.form['marker'].strip()
    obj_file = request.files.get('obj')
    mtl_file = request.files.get('mtl')
    tex_files = request.files.getlist('textures')

    if not obj_file or obj_file.filename.strip() == "":
        return "Error: OBJ file is required!", 400

    obj_path = os.path.join(UPLOAD_FOLDER, obj_file.filename)
    obj_file.save(obj_path)

    base_url = request.host_url.rstrip('/')

    obj_url = f"{base_url}/uploads/{obj_file.filename}"

    mtl_url = None
    if mtl_file and mtl_file.filename.strip() != "":
        mtl_path = os.path.join(UPLOAD_FOLDER, mtl_file.filename)
        mtl_file.save(mtl_path)
        mtl_url = f"{base_url}/uploads/{mtl_file.filename}"

    tex_urls = []
    for tex in tex_files:
        if tex and tex.filename.strip() != "":
            tex_path = os.path.join(UPLOAD_FOLDER, tex.filename)
            tex.save(tex_path)
            tex_urls.append(f"{base_url}/uploads/{tex.filename}")

    with open(MODEL_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data[marker] = {
        "obj": obj_url,
        "mtl": mtl_url,
        "textures": tex_urls
    }

    with open(MODEL_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return f"Upload thành công cho marker: {marker}<br><a href='/'>Quay lại</a>"

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/model_map.json')
def get_model_map():
    with open(MODEL_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)
    
@app.route('/check_marker', methods=['GET'])
def check_marker():
    marker = request.args.get('marker', '').strip()
    if not marker:
        return jsonify({"exists": False})
    
    with open(MODEL_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return jsonify({"exists": marker in data})


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
