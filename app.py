
#Imports dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

#Classes stored as variables
station = Base.classes.station
measurement = Base.classes.measurement

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
#This returns a list of all available routes
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<end>"
    )

@app.route("/api/v1.0/precipitation")
#This funtion returns the most recent year of preipitation data in dictionary format
def precipitation():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    twelve_month_data=session.query(measurement.date, func.max(measurement.prcp)).filter(measurement.date >=query_date).\
    group_by(measurement.date).order_by(measurement.date)
    
    precip = []
    for  date, prcp in twelve_month_data:
        prcpdict = {}
        prcpdict['date']=date
        prcpdict['prcp']=prcp
        precip.append(prcpdict)

    return jsonify(precip)

@app.route("/api/v1.0/stations")
#This function returns the station name and ID for all stations
def stations():
    session = Session(engine)
    sel = [station.name,measurement.station]
    station_join = session.query(*sel).filter(station.station==measurement.station).\
    distinct().all()
    
    station_list=list(np.ravel(station_join))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
#This function returns the most recent year of temperature data from the most active station
def tobs():
    session = Session(engine)
    query_date2 = dt.date(2017, 8, 18) - dt.timedelta(days = 365) 
    twelve_month_station_data=session.query(measurement.date, measurement.tobs).filter(measurement.date >=query_date2).\
    group_by(measurement.date).order_by(measurement.date).all()

    tobs_list=[]
    for date, tobs in twelve_month_station_data:
        tobsdict={}
        tobsdict['date']=date
        tobsdict['tobs']=tobs
        tobs_list.append(tobsdict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<yyyymmdd>")
#This function returns: min. temperature, max. temperature and avg. temperature for all stations
#starting from a user-inputter date
def start_date(yyyymmdd):
    session = Session(engine)
    start_tobs = session.query(measurement.date, func.min(measurement.tobs),func.max(measurement.tobs),\
    func.avg(measurement.tobs)).filter(measurement.date >= yyyymmdd).group_by(measurement.date).\
    order_by(measurement.date).all()

    start_tobs_list=[]
    for sdate, smin, smax, savg in start_tobs:
        start_tobs_dict={}
        start_tobs_dict["date"]=sdate
        start_tobs_dict["min"]=smin
        start_tobs_dict["max"]=smax
        start_tobs_dict["avg"]=savg
        start_tobs_list.append(start_tobs_dict)
    
    return jsonify(start_tobs_list)

@app.route("/api/v1.0/<startdate>/<enddate>")
#This function returns: min. temperature, max. temperature and avg. temperature for all stations
#starting and finishing at two user-inputted dates
def two_dates(startdate, enddate):
    session = Session(engine)
    two_date_tobs=session.query(measurement.date, func.min(measurement.tobs),func.max(measurement.tobs),\
    func.avg(measurement.tobs)).filter(measurement.date >= startdate).filter(measurement.date<= enddate).\
    group_by(measurement.date).order_by(measurement.date).all()

    two_dates_list=[]
    for tddate, tdmin, tdmax, tdavg in two_date_tobs:
        two_dates_dict={}
        two_dates_dict["date"]=tddate
        two_dates_dict["min"]=tdmin
        two_dates_dict["max"]=tdmax
        two_dates_dict["avg"]=tdavg
        two_dates_list.append(two_dates_dict)

    return jsonify(two_dates_list)

if __name__ == "__main__":
    app.run(debug=True)