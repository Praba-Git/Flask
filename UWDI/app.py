import time
from flask import Flask  
from flask import render_template
from flask_paginate import Pagination, get_page_args, get_page_parameter
from flask import (Flask, Response, jsonify, make_response, render_template,
                   request)
from datetime import datetime
import pymongo
import re


app = Flask(__name__)


client = pymongo.MongoClient("mongodb://prabmoha5:Msds123@ac-wv9ttbz-shard-00-00.o7xwskl.mongodb.net:27017,ac-wv9ttbz-shard-00-01.o7xwskl.mongodb.net:27017,ac-wv9ttbz-shard-00-02.o7xwskl.mongodb.net:27017/?ssl=true&replicaSet=atlas-z872my-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.TestUsers ## DB Creation ##
db_w = client.Weather_DB

@app.route("/")
def home():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')    
    pagination_w,total = get_weather_data(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')         
    return render_template('home.html', weatherlist=pagination_w,
                            page=page,
                            per_page=per_page,
                            pagination=pagination) 



# Common functions
def get_unique_eventid():    
    unique_id =int(db_w.TX_Dallas.find_one(sort=[("EventId",pymongo.DESCENDING)])['EventId']) + 1
    return unique_id

def get_weather_data(offset=0, per_page=10):
    w_list = list(db_w.TX_Dallas.find({}, {"_id":0}))
    return w_list[offset: offset + per_page],len(w_list)

@app.route('/weather/')
def weather_home():    
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')    
    pagination_w,total = get_weather_data(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')         
    return render_template('weather.html', weatherlist=pagination_w,
                            page=page,
                            per_page=per_page,
                            pagination=pagination) 

# add-weather record
@app.route("/add_weather",methods=["POST","GET"])
def add_weather():  
    msg='' 
    if request.method == 'POST':
        type = request.form['type']
        severity = request.form['severity']
        starttime = request.form['starttime']
        endtime = request.form['endtime']
        airportcode = request.form['airportcode']
        lat = request.form['lat']
        lang = request.form['lang']
        zipcode = request.form['zipcode']              
        id = get_unique_eventid()
        print(type)
        if type == '':
            msg = 'Please Input Type' 
        elif severity == '':
           msg = 'Please Input Severity' 
        #elif txtoffice == '':
         #  msg = 'Please Input Office' 
        else:
          myquery = {"EventId": id , "Type": type,"Severity" : severity,"StartTime(UTC)":starttime,"EndTime(UTC)":endtime,"AirportCode":airportcode,"LocationLat":lat,"LocationLng":lang,"ZipCode":zipcode}                       
          db_w.TX_Dallas.insert_one(myquery).inserted_id     
          #msg = 'New record { } created successfully'.format(db_response )
          msg = 'New weather event id '+ id + ' created successfully !'
    return jsonify(msg)

# update-weather record    
@app.route("/update_weather",methods=["POST","GET"])
def update_weather():   
    if request.method == 'POST':
        eventID = int(request.form['eventId'])
        type = request.form['type']
        severity = request.form['severity']
        starttime = datetime.strptime(request.form['starttime'], "%a, %d %b %Y %H:%M:%S %Z") 
        endtime = datetime.strptime(request.form['endtime'], "%a, %d %b %Y %H:%M:%S %Z") 
        airportcode = request.form['airportcode']
        lat = request.form['lat']
        lang = request.form['lang']
        zipcode = request.form['zipcode']
        myquery = { "EventId": eventID }
        newvalues = { "$set": { "Severity": severity,"Type": type,"StartTime(UTC)":starttime,"EndTime(UTC)":endtime,"AirportCode":airportcode ,"LocationLat": lat,"LocationLng":lang ,"ZipCode":zipcode} }                 
        print(eventID)
        db_w.TX_Dallas.update_one(myquery, newvalues) 
        msg = 'Record successfully Updated'
    return jsonify(msg)  

# method to populate the AJAX html table 
@app.route("/gridjs")
def ajax_GridJse(): 
    w_list = list(db_w.TX_Dallas.find({}, {"_id":0}))
    return  {'data': w_list}

@app.route("/ajax_add",methods=["POST","GET"])
def ajax_add():  
    msg='' 
    if request.method == 'POST':
        txtname = request.form['txtname']
        txtposition = request.form['txtposition']
        #txtoffice = request.form['txtoffice']
        print(txtname)
        if txtname == '':
            msg = 'Please Input name' 
        elif txtposition == '':
           msg = 'Please Input Position' 
        #elif txtoffice == '':
         #  msg = 'Please Input Office' 
        else:
          myquery = { "ID": txtname,"Name" : txtposition}
          #newvalues = { "$set": { "Name": txtposition } }                 
          db_response = client.TestUsers.Users.insert_one(myquery).inserted_id     
          #msg = 'New record { } created successfully'.format(db_response )
          msg = 'New record created successfully'
    return jsonify(msg)

@app.route("/delete_weather",methods=["POST","GET"])
def ajax_delete():    
    if request.method == 'POST':
        getid = int(request.form['eventID'])
        print(getid)  
        myQuery ={'EventId':getid}         
        db_w.TX_Dallas.delete_one(myQuery) 
        msg = 'Record deleted successfully'  
    return jsonify(msg) 


# Data-insights using Charts.js

@app.route("/weather_chart")
def weather_chart():
    start = datetime(2016, 1,1)
    end = datetime(2016, 1, 31)
    legend = 'Dallas Precipitation in inches'    
    #myDatetime = dateutil.parser.parse('2016-01-01T15:53:00.000+00:00')
    #from_date = ('2016-01-31T15:53:00.000+00:00')   
    chartlist = list(db_w.TX_Dallas.find({"StartTime(UTC)": {'$gt':start,'$lt':end},"Precipitation(in)":{'$gt':0.0}}))
    percipitaionY= [i['Precipitation(in)'] for i in chartlist]
    #eventDateX = [i['StartTime(UTC)'].strftime("%Y-%m-%d %H:%M:%S") for i in chartlist]
    eventDateX = [i['StartTime(UTC)'] for i in chartlist]
    # variables for populating a pie chart
    pielabelslist = list(db_w.TX_Dallas.aggregate([{'$group':{'_id':"$Type",'count':{'$count':{}}}}]))
    pielabelsX =  [i['_id'] for i in pielabelslist]
    piedataY =  [i['count'] for i in pielabelslist]
    # end 
    
    #print(len(percipitaionY))
    return render_template('weather_chart_working_copy.html', values=piedataY, labels=pielabelsX, legend=legend)
 
# weather event type distribution chart grouped by event type
@app.route("/weather_piechart")
def weather_piechart():
    #legend = 'Dallas : Distribution of weather event types from 2016 - 2021 '           
    # variables for populating a pie chart
    datalist = list(db_w.TX_Dallas.aggregate([{'$group':{'_id':"$Type",'count':{'$count':{}}}}]))
    pielabelsX =  [i['_id'] for i in datalist]
    piedataY =  [i['count'] for i in datalist]
    # end 
   # return render_template('weather_piechart.html', values=piedataY, labels=pielabelsX, legend=legend)
    return render_template('weather_piechart.html', values=piedataY, labels=pielabelsX)

# route to display weather distribution data
@app.route("/metrics")
def weather_metrics():
    legend = 'Dallas : Distribution of weather event  from 2016 - 2021 '           
    # 1.  grouped and sorted by year - Pie -Chart  will display # of events in a year
    datalist = list(db_w.TX_Dallas.aggregate([{'$group': {'_id': {'$year': "$StartTime(UTC)"}, 'count': { '$sum': 1 }}},{'$sort':{'_id':1}}]))
    labelsX =  [i['_id'] for i in datalist]
    dataY =  [i['count'] for i in datalist]
    
    # 2. grouped and sorted by month - scatter -Chart  will display # of events in a month   
    datalistmonth = list(db_w.TX_Dallas.aggregate([{'$group': {'_id': {'$month': "$StartTime(UTC)"}, 'count': { '$sum': 1 }}},{'$sort':{'_id':1}}]))    
    scatterdatamonth= [ [i['_id'],i['count']] for i in datalistmonth]  #scatter data (X,y)    

    # 3. precipitation  distribution in a bar chart
    start = datetime(2016, 1,1)
    end = datetime(2021, 12, 31)
    preciplist = list(db_w.TX_Dallas.find({"StartTime(UTC)": {'$gte':start,'$lte':end},"Precipitation(in)":{'$gt':0.0}}))
    precipY= [i['Precipitation(in)'] for i in preciplist]    
    precipYearX = [i['StartTime(UTC)'] for i in preciplist]    
    
    return render_template('weather_metrics.html', values=dataY, labels=labelsX, legend=legend,scatterdata=scatterdatamonth,barlabels=precipYearX,barvalues=precipY)
    
   