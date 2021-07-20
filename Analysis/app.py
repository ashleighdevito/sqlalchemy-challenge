#import dependencies
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

    # return home page content
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
        ***Please enter dates in the format "YYYY-MM-DD"***<br/>
        If no end date is specified, end of range will be 2017-08-23<br/>
        Dataset begins 2010-01-01
    """)


# define route to return precipitation by date
@app.route("/api/v1.0/precipitation")
def precipitation():

    #open session
    session = Session(engine)

    #definte time range
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    recent_date = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    query_date = recent_date.date() - dt.timedelta(days=365)

    #query database
    precipitation_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.date >= query_date).all()

    #close session
    session.close()

    #create dictionary of dates as keys with measured precipitation as the values
    precipitation_data = {}
    for date, prcp in precipitation_scores:
        if date in precipitation_data:
            precipitation_data[date].append(prcp)
        else:
            precipitation_data[date]= [prcp]

    #convert to json for display
    return jsonify(precipitation_data)


#define route to return a list of weather stations
@app.route("/api/v1.0/stations")
def stations():

    #open session
    session = Session(engine)

    #query the station names
    stations = session.query(Station.name).all()
    
    #close session
    session.close()

    #convert tuples into list
    all_stations = list(np.ravel(stations))

    #convert to json for display
    return jsonify(all_stations)

#define route to return temperatures Temperature statistics across the state of Hawaii over a time period
@app.route("/api/v1.0/tobs")
def tobs():
    #open session
    session = Session(engine)

    #define date ranges
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    recent_date = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    query_date = recent_date.date() - dt.timedelta(days=365)

    #query the database
    temperature = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.date >= query_date).all()

    #close session
    session.close()

    #create a list of observations
    all_temperature_records = []
    for station, date, tobs in temperature:
        temperature_dict = {'Date':'Temperature Observation'}
        temperature_dict['Date']=date
        temperature_dict['Temperature Observation']=tobs
        all_temperature_records.append(temperature_dict)
    
    #convert to json for display
    return jsonify(all_temperature_records)

#define route to return temperature statistics across the state of Hawaii over an input time period
#add default end date
@app.route("/api/v1.0/<start>/", defaults={'end':'2017-08-23'})
@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    
    #open session
    session = Session(engine)

    #define date variable from input
    query_date = start
    recent_date = end

    #query the data
    temperature_ranged_stats = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date <= recent_date).\
        filter(Measurement.date >= query_date).all()
    
    #create list of dictionaries of the statistics pulled from query
    temperature_stats = []
    for date, tmin, tmax, tavg in temperature_ranged_stats:
        summary_stats = {}
        summary_stats['Temperature Minimum:'] = tmin
        summary_stats['Temperature Maximum:'] = tmax
        summary_stats['Temperature Average:'] = tavg
        temperature_stats.append(summary_stats)
    
    #convert to json for display
    return jsonify(temperature_stats)


if __name__ == "__main__":
    app.run(debug=True)