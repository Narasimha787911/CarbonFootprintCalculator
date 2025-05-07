from datetime import datetime

from flask import (flash, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash

from app import app, db
from calculator import calculate_carbon_footprint
from models import CarbonFootprint, User
from suggestion_engine import SuggestionEngine


# Context processor to inject variables into all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    """Homepage route"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            name = request.form.get('name', '').strip() or None  # Convert empty string to None
            
            # Basic validation
            if not username or not email or not password:
                flash('Username, email and password are required', 'danger')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return render_template('register.html')
            
            # Create new user with only the required fields
            user = User(
                username=username,
                email=email,
                name=name
            )
            user.set_password(password)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            login_user(user)
            flash('Your account has been created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        # Attempt to find the user
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name or user.username}!', 'success')
            
            # Redirect to the page the user was trying to access
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing past calculations"""
    # Get user's footprint calculations
    footprints = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.created_at.desc()).all()
    return render_template('dashboard.html', footprints=footprints)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """Carbon footprint calculator form submission (adapted for Indian users)"""
    if request.method == 'POST':
        try:
            # Create a new carbon footprint record with Indian metrics
            footprint = CarbonFootprint(
                # Transportation (using kilometers for Indian context)
                car_kilometers=float(request.form.get('car_kilometers', 0)),
                car_efficiency=float(request.form.get('car_efficiency', 15)),  # km per liter (default for Indian car)
                two_wheeler_kilometers=float(request.form.get('two_wheeler_kilometers', 0)),
                two_wheeler_efficiency=float(request.form.get('two_wheeler_efficiency', 50)),  # km per liter
                auto_rickshaw_kilometers=float(request.form.get('auto_rickshaw_kilometers', 0)),
                public_transit_kilometers=float(request.form.get('public_transit_kilometers', 0)),
                flights_domestic=int(request.form.get('flights_domestic', 0)),
                flights_international=int(request.form.get('flights_international', 0)),
                
                # Home energy (adapted for Indian usage)
                electricity_kwh=float(request.form.get('electricity_kwh', 0)),
                lpg_cylinders=float(request.form.get('lpg_cylinders', 0)),
                
                # Food & consumption (with Indian diet types)
                diet_type=request.form.get('diet_type', 'vegetarian'),  # Default to vegetarian in India
                
                # Optional title
                title=request.form.get('title', 'My Carbon Footprint')
            )
            
            # Link to user if logged in
            if current_user.is_authenticated:
                footprint.user_id = current_user.id
            
            # Calculate carbon footprint
            calculate_carbon_footprint(footprint)
            
            # Save to database
            db.session.add(footprint)
            db.session.commit()
            
            # Store ID in session for results page
            session['footprint_id'] = footprint.id
            
            return redirect(url_for('results'))
            
        except Exception as e:
            app.logger.error(f"Error processing form: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
    
    return render_template('calculator.html')

@app.route('/results')
def results():
    """Display carbon footprint calculation results"""
    footprint_id = session.get('footprint_id')
    
    if not footprint_id:
        flash("Please complete the calculator first", "warning")
        return redirect(url_for('calculator'))
    
    footprint = CarbonFootprint.query.get(footprint_id)
    
    if not footprint:
        flash("Could not find your calculation results", "danger")
        return redirect(url_for('calculator'))
    
    # Calculate percentages for chart
    total = footprint.total_footprint
    if total > 0:
        transport_percent = round((footprint.transportation_footprint / total) * 100)
        home_percent = round((footprint.home_energy_footprint / total) * 100)
        food_percent = round((footprint.food_footprint / total) * 100)
    else:
        transport_percent = home_percent = food_percent = 0
    
    return render_template(
        'results.html', 
        footprint=footprint,
        transport_percent=transport_percent,
        home_percent=home_percent,
        food_percent=food_percent
    )

@app.route('/my-footprints')
@login_required
def my_footprints():
    """View user's saved carbon footprint calculations"""
    footprints = CarbonFootprint.query.filter_by(user_id=current_user.id).order_by(CarbonFootprint.created_at.desc()).all()
    return render_template('my_footprints.html', footprints=footprints)

@app.route('/footprint/<int:footprint_id>')
def view_footprint(footprint_id):
    """View a specific footprint calculation"""
    footprint = CarbonFootprint.query.get_or_404(footprint_id)
    
    # If footprint belongs to a user, only they can view it
    if footprint.user_id and (not current_user.is_authenticated or footprint.user_id != current_user.id):
        flash("You don't have permission to view this calculation", "danger")
        return redirect(url_for('index'))
    
    # Calculate percentages for chart
    total = footprint.total_footprint
    if total > 0:
        transport_percent = round((footprint.transportation_footprint / total) * 100)
        home_percent = round((footprint.home_energy_footprint / total) * 100)
        food_percent = round((footprint.food_footprint / total) * 100)
    else:
        transport_percent = home_percent = food_percent = 0
    
    return render_template(
        'results.html', 
        footprint=footprint,
        transport_percent=transport_percent,
        home_percent=home_percent,
        food_percent=food_percent
    )

@app.route('/about')
def about():
    """About page with information on methodology"""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    app.logger.error(f"Server error: {str(e)}")
    return render_template('base.html', error="Internal server error"), 500

@app.route('/api/suggestions')
@login_required
def get_suggestions():
    """Get personalized suggestions for the current user"""
    engine = SuggestionEngine()
    
    # Get user's latest footprint calculation
    latest_footprint = CarbonFootprint.query.filter_by(user_id=current_user.id)\
        .order_by(CarbonFootprint.created_at.desc())\
        .first()
    
    # Generate suggestions based on actual footprint data
    suggestions = engine.generate_suggestions(latest_footprint)
    seasonal = engine.get_seasonal_suggestions()
    
    return jsonify({
        'suggestions': suggestions,
        'seasonal_suggestions': seasonal
    })
