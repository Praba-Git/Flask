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
    return render_template("Gridjs.html")

def get_users(offset=0, per_page=10):
    users = list(db.Users.find({}, {"_id":0}))
    return users[offset: offset + per_page]

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
        starttime = request.form['starttime']
        endtime = request.form['endtime']
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


@app.route('/index/')
def index():
    userlist = db.Users.find({}, {"_id":0})
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(list(userlist))
    pagination_users = get_users(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4') 
        
    # rowCount = len(list(userlist))
    #userlist = get_users(offset=0, per_page=rowCount)
    return render_template('index_ajax.html', userlist=pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination) 

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