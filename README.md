# Student Performance Predictor (`student-app`) — DevOps CI/CD Lifecycle

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D33833.svg)](https://www.jenkins.io/)
[![Pytest](https://img.shields.io/badge/pytest-Passing-brightgreen.svg)](https://pytest.org/)

An automated, end-to-end DevOps lifecycle implementation for a Machine Learning web application predicting secondary student final grades (0–20 scale) based on academic, demographic, and behavioral features.

---

## 📁 Repository Structure

```text
MLOps ISE 2/
├── app.py                             # Flask application (Web UI + REST API /predict & /health)
├── Dockerfile                         # Production multi-stage Docker build
├── docker-compose.yml                 # Local container orchestration
├── Jenkinsfile                        # Declarative 5-stage CI/CD pipeline
├── requirements.txt                   # Pinned Python dependencies
├── pytest.ini                         # Pytest configuration
├── DevOps_ISE2_Submission_Report.md   # Complete Academic Evaluation Report (ISE 2)
├── models/
│   └── student_performance_model.joblib  # Trained scikit-learn ML pipeline
├── templates/
│   └── index.html                     # Responsive glassmorphic frontend UI
├── static/
│   └── style.css                      # Modern CSS design system
└── tests/
    └── test_app.py                    # Pytest test suite for routes & model inference
```

---

## ⚡ Quickstart Commands (Windows PowerShell)

### 1. Local Run
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest tests\test_app.py -v
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

### 2. Docker Run
```powershell
docker build -t student-app .
docker run -d -p 5000:5000 --name student-app student-app
Invoke-RestMethod -Uri http://localhost:5000/health
```

### 3. Jenkins CI/CD
Create a pipeline item pointing to your GitHub repository and branch `main`. The `Jenkinsfile` automatically handles checkout, virtual environment setup, linting, pytest validation, Docker image building, container rollout, and health checking.
