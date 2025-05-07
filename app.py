import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "a secret key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///carbon_calculator.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models
    import models
    
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Add default emission categories if needed
    from models import EmissionCategory, EmissionFactor
    
    # Check if categories already exist
    if not EmissionCategory.query.first():
        # Create Indian emission categories
        transport = EmissionCategory(name="Transportation", description="Emissions from all forms of transportation")
        energy = EmissionCategory(name="Home Energy", description="Emissions from household energy consumption")
        food = EmissionCategory(name="Food", description="Emissions from food production and consumption")
        
        db.session.add_all([transport, energy, food])
        db.session.commit()
        
        # Add emission factors for Indian context
        # Transportation factors
        car_factor = EmissionFactor(
            name="Car (Petrol)", 
            value=2.31, 
            unit="kg CO2e/liter", 
            description="Carbon emissions per liter of petrol for cars",
            category_id=transport.id
        )
        
        two_wheeler_factor = EmissionFactor(
            name="Two Wheeler", 
            value=2.31, 
            unit="kg CO2e/liter", 
            description="Carbon emissions per liter of petrol for motorcycles/scooters",
            category_id=transport.id
        )
        
        auto_rickshaw_factor = EmissionFactor(
            name="Auto Rickshaw", 
            value=0.08, 
            unit="kg CO2e/km", 
            description="Carbon emissions per kilometer for auto rickshaws",
            category_id=transport.id
        )
        
        bus_factor = EmissionFactor(
            name="Public Transit", 
            value=0.04, 
            unit="kg CO2e/km", 
            description="Carbon emissions per kilometer for buses and metro",
            category_id=transport.id
        )
        
        domestic_flight_factor = EmissionFactor(
            name="Domestic Flight", 
            value=300, 
            unit="kg CO2e/flight", 
            description="Carbon emissions for average domestic flight in India",
            category_id=transport.id
        )
        
        international_flight_factor = EmissionFactor(
            name="International Flight", 
            value=2000, 
            unit="kg CO2e/flight", 
            description="Carbon emissions for average international flight from India",
            category_id=transport.id
        )
        
        # Energy factors
        electricity_factor = EmissionFactor(
            name="Electricity", 
            value=0.82, 
            unit="kg CO2e/kWh", 
            description="Carbon emissions per kWh of electricity in India (coal heavy)",
            category_id=energy.id
        )
        
        lpg_factor = EmissionFactor(
            name="LPG Cylinder", 
            value=42, 
            unit="kg CO2e/cylinder", 
            description="Carbon emissions per standard 14.2kg LPG cylinder",
            category_id=energy.id
        )
        
        # Food factors
        vegan_factor = EmissionFactor(
            name="Vegan Diet", 
            value=1200, 
            unit="kg CO2e/year", 
            description="Annual carbon emissions for vegan diet",
            category_id=food.id
        )
        
        vegetarian_factor = EmissionFactor(
            name="Vegetarian Diet", 
            value=1500, 
            unit="kg CO2e/year", 
            description="Annual carbon emissions for vegetarian diet (common in India)",
            category_id=food.id
        )
        
        eggetarian_factor = EmissionFactor(
            name="Eggetarian Diet", 
            value=1800, 
            unit="kg CO2e/year", 
            description="Annual carbon emissions for vegetarian+eggs diet (common in India)",
            category_id=food.id
        )
        
        non_veg_factor = EmissionFactor(
            name="Non-Vegetarian Diet", 
            value=2500, 
            unit="kg CO2e/year", 
            description="Annual carbon emissions for occasional non-veg diet (typical in India)",
            category_id=food.id
        )
        
        high_non_veg_factor = EmissionFactor(
            name="High Non-Vegetarian Diet", 
            value=3500, 
            unit="kg CO2e/year", 
            description="Annual carbon emissions for frequent non-veg diet",
            category_id=food.id
        )
        
        db.session.add_all([
            car_factor, two_wheeler_factor, auto_rickshaw_factor, bus_factor,
            domestic_flight_factor, international_flight_factor,
            electricity_factor, lpg_factor,
            vegan_factor, vegetarian_factor, eggetarian_factor, 
            non_veg_factor, high_non_veg_factor
        ])
        db.session.commit()

# Import routes after app is initialized to avoid circular imports
from routes import *
