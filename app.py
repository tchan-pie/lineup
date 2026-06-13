import os
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lineup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

class DanceClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(200), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    instructor = db.Column(db.String(150))
    skill_level = db.Column(db.String(50))
    day_of_week = db.Column(db.String(20))
    time = db.Column(db.String(20))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    is_recurring = db.Column(db.Boolean, default=False)
    studio_name = db.Column(db.String(200))
    studio_address = db.Column(db.String(300))

def fetch_studios_google(api_key) :
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    studios = []
    params = {
        'query': 'dance studio Seattle, WA', 'key': api_key,}
    resp = requests.get(url, params=params)
    data = resp.json()
    studios = []
    for place in data.get('results', []):
        studios.append({
            'name': place.get('name'),
            'address': place.get('formatted_address'),
        })
    return studios

@app.route('/')
def index():
    style_filter = request.args.get('style', '').strip()
    level_filter = request.args.get('level', '').strip()
    day_filter   = request.args.get('day', '').strip()
    max_price    = request.args.get('max_price', '').strip()
    query = DanceClass.query
    if style_filter:
        query = query.filter(DanceClass.style.ilike(f'%{style_filter}%'))
    if level_filter:
        query = query.filter(DanceClass.skill_level == level_filter)
    if day_filter:
        query = query.filter(DanceClass.day_of_week == day_filter)
    if max_price:
        try:
            query = query.filter(DanceClass.price <= float(max_price))
        except ValueError:
            pass
    classes = query.all()
    styles = sorted(set(c.style for c in DanceClass.query.all() if c.style))
    return render_template('index.html',
        classes=classes,
        styles=styles,
        filters={
            'style': style_filter,
            'level': level_filter,
            'day': day_filter,
            'max_price': max_price,
        },
        total=len(classes)
    )

def sample_data():
    if DanceClass.query.count() > 0:
        return
    sample_classes = [
        DanceClass(class_name="Hip Hop Foundations", style="Hip Hop", instructor="Barb", skill_level="Intermediate", day_of_week="Monday", time="8:30 PM", price=18, description="Sharpen your grooves in this fun session!", is_recurring=True, studio_name="Velocity Dance Center", studio_address="1621 12th Ave, Seattle, WA 98122"),
        DanceClass(class_name="Afrobeats Cardio", style="Afrobeats", instructor="Zara Osei", skill_level="All Levels", day_of_week="Saturday", time="10:00 AM", price=15, description="Move to the rhythm of West African beats — no experience needed!", is_recurring=True, studio_name="Dance This! Studio", studio_address="7215 Greenwood Ave N, Seattle, WA 98103"),
        DanceClass(class_name="Jazz Funk", style="Jazz", instructor="Kenji Park", skill_level="Intermediate", day_of_week="Wednesday", time="6:00 PM", price=18, description="Commercial-style jazz with a funky twist.", is_recurring=True, studio_name="Northwest Dance Center", studio_address="320 2nd Ave W, Seattle, WA 98119"),
        DanceClass(class_name="Contemporary Foundations", style="Contemporary", instructor="Maya Chen", skill_level="Beginner", day_of_week="Tuesday", time="7:00 PM", price=18, description="Explore movement fundamentals through breath, weight, and flow.", is_recurring=True, studio_name="Velocity Dance Center", studio_address="1621 12th Ave, Seattle, WA 98122"),
        DanceClass(class_name="Salsa Social", style="Salsa", instructor="Billy", skill_level="Beginner", day_of_week="Friday", time="7:30 PM", price=15, description="Learn the basics of salsa and stay for the social dance!", is_recurring=True, studio_name="Dance This! Studio", studio_address="7215 Greenwood Ave N, Seattle, WA 98103"),
        DanceClass(class_name="Ballet Barre", style="Ballet", instructor="Sofia Reyes", skill_level="All Levels", day_of_week="Monday", time="9:30 AM", price=22, description="Classic barre work for all bodies and experience levels.", is_recurring=True, studio_name="Northwest Dance Center", studio_address="320 2nd Ave W, Seattle, WA 98119"),
    ]
    for c in sample_classes:
        db.session.add(c)
    db.session.commit()

with app.app_context():
    db.create_all()
    sample_data()
if __name__ == '__main__':
    app.run(debug=True)