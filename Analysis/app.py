#import dependancies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#generate engine to sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect a new model from the database schema
Base = automap_base()
Base.prepare(engine, reflect=True)

#save reference to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#create an app, being sure to pass __name__
app = Flask(__name__)

#define home route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    recent_date = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    query_date = recent_date.date() - dt.timedelta(days=365)
    precipitation_scores = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= recent_date).\
    filter(Measurement.date >= query_date).all()

    
    precipitation_data = {}
    for date, prcp in precipitation_scores:
        if date in precipitation_data:
            precipitation_data[date].append(prcp)
        else:
            precipitation_data[date]= [prcp]

    session.close()

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"

if __name__ == "__main__":
    app.run(debug=True)
