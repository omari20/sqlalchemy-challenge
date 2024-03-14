# Import Flask
from flask import Flask, jsonify

# Import ORM dependencies
import sqlalchemy
from pathlib import Path 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, text, inspect, func
from sqlalchemy.orm import Session 
import datetime as dt
from datetime import datetime, timedelta

################################################
# Database setup
###############################################
engine = create_engine(f'sqlite:///../Resources/hawaii.sqlite', echo=False)

# Reflect the DB into the model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
Measurement_table = Base.classes.measurement
station_table = Base.classes.station

################################################
# Flask Setup
################################################

# Create an app
app = Flask(__name__)

# Define the routes for the server
@app.route('/')
def home():
    return 'Welcome to the Climate App'


# Define precipitation information route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create session from python to DB
    session = Session(engine)

    """Retrieve last 12 months of precipitation data"""
    # Find the most recent date in the dataset
    most_recent_date = session.query(Measurement_table.date).order_by\
                (Measurement_table.date.desc()).first()

    most_recent_date = most_recent_date[0]

    # Convert the string to a date object
    # most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    # Query the database for precipitation data for the previous 12 months
    precipitation_data = session.query(Measurement_table.date, Measurement_table.prcp).\
        filter(Measurement_table.date >= func.date(most_recent_date, "-12 months")).\
        filter(Measurement_table.date <= most_recent_date).\
        order_by(Measurement_table.date).all()

   # Convert precipitation data into a dictionary
    precipitation_dict = {}
    for date, prcp in precipitation_data:
        precipitation_dict[date] = prcp

    # Close session
    session.close()

    # Jsonify data
    return jsonify(precipitation_dict)
# ---------------------------------------------------------------------------

# Define the 'List of Stations' Route
@app.route('/api/v1.0/stations')
def stations_data():
    # Create session from python to DB
    session = Session(engine)

    """Return the list of all stations"""
    stations_data = session.query(station_table).all()

    # Convert data into list
    stations_list = []
    for station in stations_data:
        station_info = [
            station.id,
            station.station,
            station.name
        ]
    
    # Append station info into stations_list
        stations_list.append(station_info)

    # Close session
    session.close()

    # Return Jsonified list
    return jsonify(stations_list)
# -------------------------------------------------------------------------

# Define TOBS route
@app.route('/api/v1.0/tobs')
def tobs():
    # Create session
    session = Session(engine)
    
    """Returns the dates and temperatures of the most active stations for 
    the previous year"""
    most_recent_date = session.query(Measurement_table.date).order_by(
        Measurement_table.date.desc()).first()[0]

    # Convert the string to a date object
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    # Extract the year from the most_recent_date
    most_recent_year = most_recent_date.year

    # Calculate the start and end dates of the previous calendar year
    start_date_of_previous_year = f"{most_recent_year - 1}-01-01"
    end_date_of_previous_year = f"{most_recent_year - 1}-12-31"

    # Query the database for temperature data for the previous calendar year
    temperature_data = session.query(Measurement_table.date, Measurement_table.tobs).\
        filter(Measurement_table.date >= start_date_of_previous_year).\
        filter(Measurement_table.date <= end_date_of_previous_year).\
        order_by(Measurement_table.date).all()
    
    # Convert temperature data into a dictionary
    temp_dict = {str(date): tobs for date, tobs in temperature_data}

    # Close session
    session.close()

    # Jsonify data
    return jsonify(temp_dict)
# ---------------------------------------------------------------------------------------
# function wrapper
# url, endpoint,
@app.route('/api/v1.0/<start>')
def temperature_start(start):
    # Create session from python to DB
    session = Session(engine)

    # Query for temperature data
    temperature_data = session.query(func.min(Measurement_table.tobs),
                                     func.avg(Measurement_table.tobs),
                                     func.max(Measurement_table.tobs)).\
        filter(Measurement_table.date >= start).all()

    # Close session
    session.close()

    # Extract temperature data
    tmin, tavg, tmax = temperature_data[0]

    # Return JSON with temperature data
    return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})

@app.route('/api/v1.0/<start>/<end>')
def temperature_start_end(start, end):
    start = "2021-01-01"
    # Create session from python to DB
    session = Session(engine)

    # Query for temperature data
    temperature_data = session.query(func.min(Measurement_table.tobs),
                                     func.avg(Measurement_table.tobs),
                                     func.max(Measurement_table.tobs)).\
        filter(Measurement_table.date >= start).\
        filter(Measurement_table.date <= end).all()

    # Close session
    session.close()

    # Extract temperature data
    tmin, tavg, tmax = temperature_data[0]

    # Return JSON with temperature data
    return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})
# --------------------------------------------------------------



# Define main behaviour
if __name__ == '__main__':
    app.run(debug=True)