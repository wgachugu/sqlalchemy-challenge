import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to my Homepage!<br/>"
        f"Available Routes:<br/>"
        f"precipitation = /api/v1.0/precipitation<br/>"
        f"stations = /api/v1.0/stations<br/>"
        f"temperature observations = /api/v1.0/tobs<br/>"
        f"start route = /api/v1.0/<start><br/>"
        f"start/end route = /api/v1.0/<start>/<end><br/>"
        f"NOTE: date format for start route and start/end route parameters is MMDDYYYY"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return json with the date as the key and the value as precipitation for the last year"""
    # Query all precipitation data for the last year in the database
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    last_year_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        last_year_precipitation.append(prcp_dict)

    return jsonify(last_year_precipitation)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations in the database
    results = session.query(Measurement.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return json list of temperature observations for the previous year"""
    # Query the dates and temperatures from the most active station for the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-01-01').\
        filter(Measurement.date < '2017-01-01').all()

    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Fetch the minimum temperature, the average temperature, and the maximum temperature
       for a specified timeframe"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= start).all()
    
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*selection).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)
    
       
if __name__ == '__main__':
    app.run(debug=True)