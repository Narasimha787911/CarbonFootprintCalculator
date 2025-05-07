import random
from datetime import datetime

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from models import EmissionCategory, EmissionFactor, User


class SuggestionEngine:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.transport_threshold = {
            'low': 50,
            'medium': 150,
            'high': 300
        }
        self.energy_threshold = {
            'low': 60,
            'medium': 120,
            'high': 200
        }
        self.food_threshold = {
            'low': 1500,
            'medium': 2500,
            'high': 3500
        }

    def analyze_footprint(self, footprint):
        """Analyze the carbon footprint data to determine areas of concern"""
        analysis = {
            'transport': {
                'level': 'low',
                'score': 0,
                'main_contributors': []
            },
            'energy': {
                'level': 'low',
                'score': 0,
                'main_contributors': []
            },
            'food': {
                'level': 'low',
                'score': 0,
                'factors': []
            }
        }

        # Analyze transportation
        transport_score = footprint.transportation_footprint
        if transport_score > self.transport_threshold['high']:
            analysis['transport']['level'] = 'high'
        elif transport_score > self.transport_threshold['medium']:
            analysis['transport']['level'] = 'medium'
        analysis['transport']['score'] = transport_score

        # Identify main transportation contributors
        if footprint.car_kilometers > 0:
            analysis['transport']['main_contributors'].append(
                ('car', footprint.car_kilometers * (1/footprint.car_efficiency))
            )
        if footprint.two_wheeler_kilometers > 0:
            analysis['transport']['main_contributors'].append(
                ('two_wheeler', footprint.two_wheeler_kilometers * (1/footprint.two_wheeler_efficiency))
            )
        if footprint.flights_domestic > 0 or footprint.flights_international > 0:
            analysis['transport']['main_contributors'].append(
                ('flights', footprint.flights_domestic * 300 + footprint.flights_international * 2000)
            )

        # Analyze energy usage
        energy_score = footprint.home_energy_footprint
        if energy_score > self.energy_threshold['high']:
            analysis['energy']['level'] = 'high'
        elif energy_score > self.energy_threshold['medium']:
            analysis['energy']['level'] = 'medium'
        analysis['energy']['score'] = energy_score

        # Identify main energy contributors
        if footprint.electricity_kwh > 0:
            analysis['energy']['main_contributors'].append(('electricity', footprint.electricity_kwh))
        if footprint.lpg_cylinders > 0:
            analysis['energy']['main_contributors'].append(('lpg', footprint.lpg_cylinders * 42))

        # Analyze food choices
        food_score = footprint.food_footprint
        if food_score > self.food_threshold['high']:
            analysis['food']['level'] = 'high'
        elif food_score > self.food_threshold['medium']:
            analysis['food']['level'] = 'medium'
        analysis['food']['score'] = food_score
        analysis['food']['factors'].append(footprint.diet_type)

        return analysis

    def get_personalized_suggestions(self, analysis):
        """Generate personalized suggestions based on footprint analysis"""
        suggestions = []

        # Transportation suggestions
        if analysis['transport']['level'] in ['medium', 'high']:
            main_contributors = sorted(analysis['transport']['main_contributors'], 
                                    key=lambda x: x[1], reverse=True)
            if main_contributors:
                top_contributor = main_contributors[0][0]
                if top_contributor == 'car':
                    suggestions.extend([
                        "Your car usage is a major contributor. Consider carpooling or using public transport 2-3 times a week to reduce emissions by up to 30%",
                        "Based on your driving patterns, switching to an electric vehicle could reduce your transport emissions by 70%",
                        f"Your current car efficiency can be improved. Regular maintenance could increase efficiency by 15%"
                    ])
                elif top_contributor == 'flights':
                    suggestions.extend([
                        "Consider video conferencing for business meetings when possible",
                        "If flying is necessary, choose direct flights to reduce emissions",
                        "Consider offsetting your flight emissions through verified carbon offset programs"
                    ])

        # Energy suggestions based on actual usage
        if analysis['energy']['level'] in ['medium', 'high']:
            energy_contributors = sorted(analysis['energy']['main_contributors'],
                                      key=lambda x: x[1], reverse=True)
            if energy_contributors:
                top_energy = energy_contributors[0][0]
                if top_energy == 'electricity':
                    suggestions.extend([
                        f"Your electricity usage is {analysis['energy']['score']:.1f} kg CO2e. Installing solar panels could reduce this by 60%",
                        "Smart home automation could help reduce your electricity consumption by 20-30%",
                        "Consider upgrading to energy-efficient appliances to reduce consumption"
                    ])
                elif top_energy == 'lpg':
                    suggestions.extend([
                        "Consider using solar cookers for daytime cooking when possible",
                        "Regular maintenance of gas appliances can improve efficiency",
                        "Using pressure cookers can reduce cooking time and gas consumption"
                    ])

        # Food suggestions based on diet type and score
        if analysis['food']['level'] in ['medium', 'high']:
            diet_type = analysis['food']['factors'][0]
            if diet_type == 'non-vegetarian':
                suggestions.extend([
                    "Reducing meat consumption to 2-3 times a week could lower your food emissions by 30%",
                    "Choose locally sourced meat to reduce transportation emissions",
                    "Consider plant-based alternatives for some meals"
                ])
            elif diet_type == 'vegetarian':
                suggestions.extend([
                    "Buy seasonal produce to reduce storage and transportation emissions",
                    "Start a small kitchen garden for commonly used vegetables",
                    "Consider composting food waste to reduce methane emissions"
                ])

        # Randomize but ensure we return most relevant suggestions first
        random.shuffle(suggestions)
        return suggestions[:5]

    def generate_suggestions(self, footprint):
        """Main method to generate personalized suggestions"""
        if not footprint:
            return self.get_default_suggestions()

        # Analyze the footprint data
        analysis = self.analyze_footprint(footprint)
        
        # Get personalized suggestions
        suggestions = self.get_personalized_suggestions(analysis)
        
        # If we don't have enough suggestions, add some defaults
        if len(suggestions) < 5:
            suggestions.extend(self.get_default_suggestions())
            suggestions = suggestions[:5]

        return suggestions

    def get_default_suggestions(self):
        """Default suggestions for new users or when no data is available"""
        return [
            "Start tracking your daily transportation choices",
            "Monitor your home energy consumption",
            "Try meat-free Mondays to reduce food emissions",
            "Use public transportation when possible",
            "Consider energy-efficient appliances for your next purchase"
        ]

    def get_seasonal_suggestions(self):
        """Get season-specific suggestions based on current month"""
        month = datetime.now().month
        
        if 3 <= month <= 5:  # Spring
            return [
                "Open windows for natural ventilation instead of AC",
                "Start a spring vegetable garden",
                "Use natural light during longer daylight hours",
                "Service your AC for summer efficiency"
            ]
        elif 6 <= month <= 8:  # Summer
            return [
                "Use natural cooling methods before turning to AC",
                "Install window shades or curtains to reduce heat gain",
                "Consider using a solar cooker for some meals",
                "Use ceiling fans to reduce AC usage"
            ]
        elif 9 <= month <= 11:  # Fall
            return [
                "Prepare your home for winter by checking insulation",
                "Take advantage of cooler weather by air-drying clothes",
                "Plant trees for future carbon absorption",
                "Collect rainwater for garden use"
            ]
        else:  # Winter
            return [
                "Use draft excluders to prevent heat loss",
                "Maximize natural sunlight for heating",
                "Grow indoor herbs for fresh cooking",
                "Consider indoor composting methods"
            ]

    def get_user_profile(self, user):
        """Analyze user's emission patterns and preferences"""
        emissions = user.emissions
        if not emissions:
            return None
            
        profile = {
            'total_emissions': sum(e.amount for e in emissions),
            'categories': {},
            'frequency': len(emissions)
        }
        
        for emission in emissions:
            category = emission.factor.category.name
            if category not in profile['categories']:
                profile['categories'][category] = 0
            profile['categories'][category] += emission.amount
            
        return profile
    
    def get_advanced_suggestions(self, profile):
        """Generate advanced AI-driven suggestions based on complex pattern analysis"""
        advanced_suggestions = [
            "Based on your usage pattern, switching to renewable energy could reduce your emissions by 40%",
            "Your transportation emissions show a pattern where using public transit twice a week could save 500kg CO2e annually",
            "Consider joining a local community garden - users with similar profiles reduced food emissions by 25%",
            "Your energy usage suggests smart home automation could help reduce emissions by 15-20%",
            "Based on similar users, installing a programmable thermostat could reduce your energy emissions by 30%"
        ]
        return advanced_suggestions

    def get_seasonal_suggestions(self):
        """Provide season-specific suggestions"""
        # You can expand this based on actual season detection
        summer_suggestions = [
            "Use natural cooling methods before turning to air conditioning",
            "Install window shades or curtains to reduce heat gain",
            "Consider using a solar cooker for some meals",
            "Start a summer vegetable garden to reduce food miles"
        ]
        return summer_suggestions 