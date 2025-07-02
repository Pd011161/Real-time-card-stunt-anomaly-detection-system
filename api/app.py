from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
import string
import io
from skimage.metrics import structural_similarity as ssim
import threading

# app = Flask(__name__)
app = Flask(__name__, template_folder="../templates", static_folder="../static")

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

reference_image_path = None
processing_enabled = False
reference_image = None
labels_and_scores = []
latest_live_frame = None  # <<== สำหรับเก็บเฟรมล่าสุดที่ browser ส่งมา
lock = threading.Lock()

# Detection config
threshold = 0.45
box_size = (5, 5)
grid_size = (25, 50)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def align_images(image1, image2):
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(5000)
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    num_good_matches = int(len(matches) * 0.15)
    good_matches = matches[:num_good_matches]
    if len(good_matches) < 4:
        return image1
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    height, width, channels = image2.shape
    aligned_image = cv2.warpPerspective(image1, matrix, (width, height))
    return aligned_image

def image_transformation(reference_image, captured_image):
    reference_image = cv2.resize(reference_image, (250, 125))
    captured_image = cv2.resize(captured_image, (250, 125))
    return reference_image, captured_image

def SSIM_Score(captured_image, reference_image, rows, cols, box_height, box_width, scr):
    differences = []
    for i in range(rows):
        for j in range(cols):
            ref_box = reference_image[i * box_height:(i + 1) * box_height, j * box_width:(j + 1) * box_width]
            cap_box = captured_image[i * box_height:(i + 1) * box_height, j * box_width:(j + 1) * box_width]
            score, _ = ssim(ref_box, cap_box, full=True, channel_axis=-1, win_size=3)
            if score < scr:
                differences.append((i, j, score))
    return differences

def ssim_position(differences, captured_image, box_height, box_width):
    global labels_and_scores
    labels_and_scores = []
    y_labels = list(string.ascii_uppercase)
    for (i, j, score) in differences:
        cv2.rectangle(captured_image, (j * box_width, i * box_height),
                      ((j + 1) * box_width, (i + 1) * box_height), (0, 0, 255), 1)
        y_label = y_labels[i % 26]
        x_label = j + 1
        label = f"{y_label}{x_label}"
        labels_and_scores.append((label, score))
    return captured_image

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global reference_image_path, reference_image
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = file.filename
        reference_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(reference_image_path)
        reference_image = cv2.imread(reference_image_path)
        return jsonify({'filepath': reference_image_path}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/toggle_processing', methods=['POST'])
def toggle_processing():
    global processing_enabled
    processing_enabled = request.json.get('enable', False)
    return jsonify({'processing_enabled': processing_enabled})

@app.route('/live_frame', methods=['POST'])
def live_frame():
    global latest_live_frame
    if 'frame' not in request.files:
        return '', 204
    file = request.files['frame']
    img_bytes = file.read()
    npimg = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if frame is not None:
        latest_live_frame = frame
    return '', 204

# def process_live_frame():
#     global latest_live_frame, reference_image, labels_and_scores
#     if not processing_enabled or reference_image is None or latest_live_frame is None:
#         labels_and_scores = []
#         return None

#     aligned_frame = align_images(latest_live_frame, reference_image)
#     transformed_ref, transformed_frame = image_transformation(reference_image, aligned_frame)
#     differences = SSIM_Score(transformed_frame, transformed_ref, grid_size[0], grid_size[1], box_size[0], box_size[1], threshold)
#     highlighted_frame = ssim_position(differences, transformed_frame, box_size[0], box_size[1])
#     return highlighted_frame
def process_live_frame():
    global latest_live_frame, reference_image, labels_and_scores, latest_result_frame
    if not processing_enabled or reference_image is None or latest_live_frame is None:
        labels_and_scores = []
        with lock:
            latest_result_frame = None
        return None

    aligned_frame = align_images(latest_live_frame, reference_image)
    transformed_ref, transformed_frame = image_transformation(reference_image, aligned_frame)
    differences = SSIM_Score(transformed_frame, transformed_ref, grid_size[0], grid_size[1], box_size[0], box_size[1], threshold)
    highlighted_frame = ssim_position(differences, transformed_frame, box_size[0], box_size[1])
    with lock:
        latest_result_frame = highlighted_frame
    return highlighted_frame

@app.route('/live_result_image')
def live_result_image():
    global latest_result_frame
    with lock:
        frame = latest_result_frame.copy() if latest_result_frame is not None else None
    if frame is None:
        return '', 204
    success, img_encoded = cv2.imencode('.jpg', frame)
    if not success:
        return '', 500
    return send_file(io.BytesIO(img_encoded.tobytes()), mimetype='image/jpeg')

@app.route('/differences')
def get_differences():
    process_live_frame()
    global labels_and_scores
    return jsonify({
        'count': len(labels_and_scores),
        'positions': [{'label': label, 'score': score} for label, score in labels_and_scores]
    })

@app.route('/process_image', methods=['POST'])
def process_image():
    global reference_image
    try:
        if 'captured' not in request.files:
            return jsonify({'error': 'No captured image uploaded.'}), 400
        if reference_image is None:
            return jsonify({'error': 'No reference image uploaded yet.'}), 400

        file = request.files['captured']
        img_bytes = file.read()
        npimg = np.frombuffer(img_bytes, np.uint8)
        captured_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if captured_image is None:
            return jsonify({'error': 'Cannot read uploaded image.'}), 400

        aligned_frame = align_images(captured_image, reference_image)
        transformed_ref, transformed_frame = image_transformation(reference_image, aligned_frame)
        differences = SSIM_Score(transformed_frame, transformed_ref, grid_size[0], grid_size[1], box_size[0], box_size[1], threshold)
        highlighted_frame = ssim_position(differences, transformed_frame, box_size[0], box_size[1])
        success, img_encoded = cv2.imencode('.jpg', highlighted_frame)
        if not success:
            return jsonify({'error': 'Image encoding failed.'}), 500

        return send_file(
            io.BytesIO(img_encoded.tobytes()),
            mimetype='image/jpeg',
            as_attachment=False
        )
    except Exception as e:
        import traceback
        print("Exception in /process_image:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5003)
    # app.run()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)