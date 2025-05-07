def calculate_carbon_footprint(footprint):
    """Calculate carbon footprint based on input data adapted for Indian context
    
    Args:
        footprint: CarbonFootprint model instance with input data
        
    Returns:
        Updated footprint object with calculated emissions
    """
    # Transportation calculations
    # Car: Indian emissions factor ~0.15 kg CO2e per km (depends on fuel efficiency)
    # Average Indian car fuel efficiency ~15 km/L
    car_emissions = (footprint.car_kilometers / (footprint.car_efficiency or 15)) * 2.31 if footprint.car_kilometers > 0 else 0
    
    # Two-wheeler emissions ~0.07 kg CO2e per km (depends on efficiency)
    # Average Indian bike/scooter fuel efficiency ~50 km/L
    two_wheeler_emissions = (footprint.two_wheeler_kilometers / (footprint.two_wheeler_efficiency or 50)) * 2.31 if footprint.two_wheeler_kilometers > 0 else 0
    
    # Auto rickshaw: ~0.08 kg CO2e per km
    auto_rickshaw_emissions = footprint.auto_rickshaw_kilometers * 0.08
    
    # Public transit: ~0.04 kg CO2e per passenger km (bus/metro in India)
    public_transit_emissions = footprint.public_transit_kilometers * 0.04
    
    # Flights (kg CO2e per flight) - adjusted for Indian routes
    flight_domestic_emissions = footprint.flights_domestic * 300  # ~300kg per domestic flight
    flight_international_emissions = footprint.flights_international * 2000  # ~2000kg per international flight
    
    # Sum transportation emissions
    transportation_footprint = (
        car_emissions + 
        two_wheeler_emissions +
        auto_rickshaw_emissions +
        public_transit_emissions + 
        flight_domestic_emissions + 
        flight_international_emissions
    )
    
    # Home energy calculations
    # Electricity: ~0.82 kg CO2e per kWh (India average - coal heavy)
    electricity_emissions = footprint.electricity_kwh * 0.82
    
    # LPG cylinders: ~42 kg CO2e per 14.2kg cylinder (standard in India)
    lpg_emissions = footprint.lpg_cylinders * 42
    
    # Sum home energy emissions
    home_energy_footprint = electricity_emissions + lpg_emissions
    
    # Food & consumption calculations (simplified based on diet type for Indian context)
    diet_emissions = {
        'vegan': 1200,  # Annual kg CO2e for vegan diet
        'vegetarian': 1500,  # Annual kg CO2e for vegetarian diet (common in India)
        'eggetarian': 1800,  # Annual kg CO2e for vegetarian+eggs diet (common in India)
        'non-vegetarian': 2500,  # Annual kg CO2e for occasional non-veg diet (typical in India)
        'high-non-vegetarian': 3500  # Annual kg CO2e for frequent non-veg diet
    }
    
    # Get annual diet emissions
    food_footprint = diet_emissions.get(footprint.diet_type, 1500)  # Default to vegetarian for India
    
    # Calculate total footprint
    total_footprint = transportation_footprint + home_energy_footprint + food_footprint
    
    # Update footprint object
    footprint.transportation_footprint = round(transportation_footprint, 2)
    footprint.home_energy_footprint = round(home_energy_footprint, 2)
    footprint.food_footprint = round(food_footprint, 2)
    footprint.total_footprint = round(total_footprint, 2)
    
    return footprint
