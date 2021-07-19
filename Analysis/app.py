#import dependancies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from sqlalchemy.sql.operators import json_path_getitem_op

#generate engine to sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

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

    return ("""
        Available Routes:<br/>
        For measured precipitation values by date over the final year of data:<br/>
        /api/v1.0/precipitation<br/>
        <br/>
        For a list of weather stations across the state of Hawaii:<br/>
        /api/v1.0/stations<br/>
        <br/>
        For a list of temperature observations from the Waihee Station by date over the final year of data:<br/>
        /api/v1.0/tobs<br/>
        <br/>
        For Temperature statistics across the state of Hawaii over a time period:<br/>
        /api/v1.0/start_date/end_date<br/>
        Please enter dates in the format "YYYY-MM-DD"<br/>
        If no end date is specified, end of range will be 2017-08-23<br/>
        Dataset begins 2010-01-01
    """)


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

    session.close()

    precipitation_data = {}
    for date, prcp in precipitation_scores:
        if date in precipitation_data:
            precipitation_data[date].append(prcp)
        else:
            precipitation_data[date]= [prcp]

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(Station.name).all()

    session.close()

    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    recent_date = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    query_date = recent_date.date() - dt.timedelta(days=365)

    temperature = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.date >= query_date).all()

    session.close()

    all_temperature_records = []
    for station, date, tobs in temperature:
        temperature_dict = {'Date':'Temperature Observation'}
        temperature_dict['Date']=date
        temperature_dict['Temperature Observation']=tobs
        all_temperature_records.append(temperature_dict)
    
    return jsonify(all_temperature_records)

@app.route("/api/v1.0/<start>/", defaults={'end':'2017-08-23'})
@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    session = Session(engine)

    query_date = start
    recent_date = end

    temperature_ranged_stats = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.date >= query_date).all()
    
    temperature_stats = []
    for date, tmin, tmax, tavg in temperature_ranged_stats:
        summary_stats = {}
        summary_stats['Temperature Minimum:'] = tmin
        summary_stats['Temperature Maximum:'] = tmax
        summary_stats['Temperature Average:'] = tavg
        temperature_stats.append(summary_stats)
    
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)