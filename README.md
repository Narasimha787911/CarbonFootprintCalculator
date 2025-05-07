# Carbon Emission Calculator

## Overview
The **Carbon Emission Calculator** is a web-based application designed to track and calculate carbon emissions based on various user activities. It utilizes **Flask** as the backend framework and **SQLite** as the database. The application allows users to log activities and determine their carbon footprint.

## Features
- User authentication and management
- Activity logging for carbon footprint calculation
- Dynamic carbon emission calculation based on predefined emission factors
- Database storage using **SQLite**
- Simple and user-friendly interface

## Technologies Used
- **Python** (Flask, SQLAlchemy)
- **SQLite** (Database management)
- **HTML, CSS, JavaScript** (Frontend)
- **Jinja2** (Templating engine for Flask)

## Installation
To set up and run the Carbon Emission Calculator on your local machine, follow these steps:

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Flask (`pip install flask`)
- Flask-SQLAlchemy (`pip install flask_sqlalchemy`)

### Steps to Install and Run
1. Clone the repository:
   ```bash
   git clone https://github.com/Narasimha787911/CarbonCalculator.git
   cd CarbonCalculator
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python app.py
   ```
   This will create `carbon_emission.db` if it doesn’t exist.
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage
- **Register/Login**: Users can create an account and log in.
- **Add Activity**: Enter activity details like type, duration, and emission factor.
- **View Emissions**: The application calculates and displays total carbon emissions.

## Contributing
We welcome contributions to enhance CarbonCalculator. Please follow these steps:

1. **Fork the Repository**: Click the "Fork" button on the top right corner of this page.

2. **Create a New Branch**:
   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes**:
   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**:
   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**: Navigate to your forked repository and click the "New Pull Request" button.


