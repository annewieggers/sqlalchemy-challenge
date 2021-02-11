import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(bind=engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

# @app.route("/") - List all routes that are available.

@app.route("/")
def home_page():
    """List all routes."""
    return (
        f"All Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start-end<br/>"
    )


# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation/")

def precipitation():
   
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation amounts"""
    
    # Retrieve precipitation data 
    precip = (session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date))

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_list = []
    for result in precip:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]
        prcp_list.append(prcp_dict)
        
    return jsonify(prcp_list)


# /api/v1.0/stations Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations/")

def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all active stations"""
    
    # Query all active stations
    
    results_stations = session.query(Station).all()    
     
    #session.close()
    
    list_stations = []

    for station in results_stations:

        station_dict = {}

        station_dict["id"] = station.id

        station_dict["station"] = station.station

        station_dict["name"] = station.name

        station_dict["latitude"] = station.latitude

        station_dict["longitude"] = station.longitude

        station_dict["elevation"] = station.elevation

        list_stations.append(station_dict)

    return jsonify(list_stations)



# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")

def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all tobs"""
    
    # Determine the last date and year ago
    latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    latest = latest_date[0]
    
    # Calculate the date 1 year ago from the last data point in the database
    latest = dt.datetime.strptime(latest, '%Y-%m-%d')
    latest = latest.date()
    year_ago = latest - relativedelta(days=365)
    
    # Determine active stations and order by most active
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()    
        
    # Identify most active station
    most_active = active_stations[0][0]
    
    # Query the dates and temperature observations of the most active station for the last year of data.
    
    temp_data = session.query(Measurement.date, Measurement.tobs). filter(Measurement.date >= year_ago).filter(Measurement.station==most_active).all()
    
    session.close()
    
    # Return a list of all tobs
    all_tobs = []
    for tob in temp_data:
        tobs_dict = {}
        tobs_dict["date"] = tob.date
        tobs_dict["tobs"] = tob.tobs
        all_tobs.append(tobs_dict)    
        
    return jsonify(all_tobs)



# /api/v1.0/<start> 
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/start")
def start():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Start date"""  
    
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    latest = latest_date[0]
    
    # Calculate the date 1 year ago from the last data point in the database
    latest = dt.datetime.strptime(latest, '%Y-%m-%d')
    latest = latest.date()
    year_ago = latest - relativedelta(days=365)
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()  
    
    most_active = active_stations[0][0]
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station==most_active).filter(Measurement.date >= year_ago).all()

    session.close()
    
    return jsonify(results)    

#  /api/v1.0/<api/v1.0/start-end
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/start-end")
def start_end():

    # Create our session (link) from Python to the DB        
    session = Session(engine) 
           
    """Start - End date"""
    
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    latest = latest_date[0]
    
    # Calculate the date 1 year ago from the last data point in the database
    latest = dt.datetime.strptime(latest, '%Y-%m-%d')
    latest = latest.date()
    year_ago = latest - relativedelta(days=365) 
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()  
    
    most_active = active_stations[0][0]
           
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station==most_active).filter(Measurement.date >= year_ago).filter(Measurement.date <= latest).all()
    
    session.close() 
    
           
    return jsonify(results)


    
if __name__ == '__main__':
    app.run(debug=True)
    
