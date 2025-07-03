# Real-time Card Stunt Anomaly Detection System

![App Screenshot](static/uploads/screenshot.png)

A web app for **real-time anomaly detection** on card stunt grids using webcam or uploaded images.  
Built with **Flask, OpenCV, SSIM, and TailwindCSS**.  
Detects and highlights areas of difference based on grid cells, with both visual and text summaries.

---

## 🚀 Features

- **Live Detection:** Realtime anomaly detection via your webcam.
- **Image Detection:** Upload images to compare against a reference.
- **Grid-based SSIM:** Finds differences at fine detail, cell by cell.
- **Intuitive UI:** Modern, responsive, and easy to use.
- **Visual + Text Output:** Highlights anomaly locations (A1, B3, ...) and displays as summary.

---

## 🖥️ Tech Stack

- **Backend:** Flask, OpenCV, scikit-image (SSIM)
- **Frontend:** HTML, TailwindCSS, JavaScript
- **Container:** Docker-ready

---

## ⚡️ Getting Started

**3 Steps to run:**

```bash
# 1. Build Docker image
docker build -t anomaly-detection-flask-app .

# 2. Run Docker container
docker run -d -p 8080:8080 anomaly-detection-flask-app

# 3. Open your browser
http://localhost:8080/
```

🕹️ How to Use

1. **Upload a Reference Image** (standard card stunt grid)
2. **Select Detection Mode:**
    - **Live Detection:** Use your webcam (click "Start Detection")
    - **Image Detection:** Upload an image to compare
3. **View Results:**
    - **Visual:** Highlighted differences in the grid
    - **Text:** List of grid positions with anomalies (e.g., A1, B12)

---

📁 Project Structure

```bash
.
├── app.py                # Flask backend
├── requirements.txt
├── templates/
│   └── home.html         # Main web page
├── static/
│   ├── uploads/          # Uploaded images
│   └── ...               # Assets
├── Dockerfile            # (Optional, for containerization)
└── README.md
```

---

📝 Example Usage

Live Detection

- Upload a reference image
- Select **"Live Detection"** and click **"Start Detection"**
- The app will highlight and summarize grid differences in real time

Image Detection

- Upload a reference image
- Select **"Image Detection"** and upload a target image
- The app compares, highlights, and lists grid differences

---

⚠️ Notes

- Only `.jpg` and `.png` files are supported.
- The reference and target images should be as similar in size and perspective as possible.
- Designed for use cases with grid-based layouts (e.g., card stunts, pixel art displays).

---

📝 Quick Summary

Flask + OpenCV app for real-time and image-based anomaly detection on card stunt grids using grid-based SSIM.
