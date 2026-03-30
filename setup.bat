@echo off
echo ==========================================
echo  FraudShield - Insurance Fraud Detection
echo  Setup Script
echo ==========================================
echo.

echo Checking Python...
python --version
echo.

echo [1/3] Upgrading pip and installing dependencies...
python -m pip install --upgrade pip
python -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Flask-Bcrypt python-dotenv scikit-learn imbalanced-learn pandas numpy joblib python-docx email-validator
if errorlevel 1 (
    echo.
    echo ==========================================
    echo  pip install failed. Trying conda instead...
    echo ==========================================
    conda install -y scikit-learn pandas numpy joblib flask
    python -m pip install Flask-SQLAlchemy Flask-Login Flask-WTF Flask-Bcrypt python-dotenv imbalanced-learn python-docx email-validator
)
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo FIX: Install Python 3.12 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo Then run this script again.
    pause
    exit /b 1
)
echo.

echo [2/3] Training ML model...
python train_model.py
if errorlevel 1 (
    echo ERROR: Model training failed!
    pause
    exit /b 1
)
echo.

echo [3/3] Starting server...
echo.
echo ==========================================
echo  Server is running at: http://127.0.0.1:5000
echo  Open this URL in your browser
echo  Press Ctrl+C to stop the server
echo ==========================================
echo.
python run.py
pause
