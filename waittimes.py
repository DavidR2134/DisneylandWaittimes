import json
import mysql.connector
import os
import requests
from ride import Ride

SQL_USER = os.environ.get('SQL_USER')
SQL_PASS = os.environ.get('SQL_PASS')

PATH = '/home/davidr/share/Share/'

def checkWaitTimes(index, waitTimes):
    if index == 0:
        with open(PATH + 'waittimesDisneyland.json', 'w') as f:
            r = requests.get(waitTimes)
            json.dump(r.json(), f)

    else:
        with open(PATH + 'waittimesCaAdventure.json', 'w') as f:
            r = requests.get(waitTimes)
            json.dump(r.json(), f)



def checkLandID(ride_name):
    land_mapping = {
        'Main Street U.S.A': 1,
        'Adventureland': 2,
        'Frontierland': 3,
        'Fantasyland': 4,
        'Tomorrowland': 5,
        'Critter Country': 6,
        'New Orleans Square': 7,
        "Mickey's Toontown": 8,
        "Star Wars: Galaxy's Edge": 9,
        'Buena Vista Street': 10,
        'Hollywood Land': 11,
        'Grizzly Peak': 12,
        'Avengers Campus': 13,
        'Cars Land': 14,
        'Paradise Gardens Park': 15,
        'Pixar Pier': 16
    }

    return land_mapping.get(ride_name, None)


def createRides(file, rides, rideNames):
    for index, i in enumerate(rides):
        for j in range(len(i['rides'])):
            name = i['rides'][j]['name']
            isOpen = i['rides'][j]['is_open']
            waitTime = i['rides'][j]['wait_time']
            lastUpdated = (i['rides'][j]['last_updated'][:10] + " " + i['rides'][j]['last_updated'][11:-5])
            landID = checkLandID(i['name'])
            r = Ride(name, isOpen, waitTime, lastUpdated, landID)
            rideNames.append(r)

def connect_to_db(rideNames):
    mydb = mysql.connector.connect(
        host='localhost',
        user=SQL_USER,
        password=SQL_PASS,
        database='disney'
    )


    mycursor = mydb.cursor()
    sql = "SELECT id, name FROM ride;"
    mycursor.execute(sql)
    results = mycursor.fetchall()

    #Collect ride names and ID's
    mydict = {}

    #Add \\ for rides with apostrophe's
    for i in results:
        if "'" in i[1]:
            mydict[i[1].replace("'", "\\'")] = i[0]
        else:
            mydict[i[1]] = i[0]


    #Update Ride wait times
    for i in range(len(rideNames)):
        sql = f"UPDATE ride SET name = '{rideNames[i].name}' , isOpen = {rideNames[i].isOpen}, waitTime = {rideNames[i].waitTime}, lastUpdated = '{rideNames[i].lastUpdated}', landID = {rideNames[i].landID} WHERE id = {mydict[rideNames[i].name]}"
        mycursor.execute(sql)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")

    #Add Ride wait times to Transaction table - Average tracking
    for i in range(len(rideNames)):

        sql = f"INSERT INTO transaction(name, isOpen, waitTime, lastUpdated, landID, rideid) VALUES ({rideNames[i]}, {mydict[rideNames[i].name]})"
        mycursor.execute(sql)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")






def main():

    rideNames= []

    #Get ride wait times from Disneyland
    parks = 'https://queue-times.com/en-US/parks.json'
    parks = [16,17]
    index = 0
    waitTimes = f'https://queue-times.com/en-US/parks/{parks[index]}/queue_times.json'
    checkWaitTimes(index, waitTimes)
    f = open(PATH + 'waittimesDisneyland.json')
    data = json.load(f)

    rides = data['lands']
    createRides(f, rides, rideNames)
    f.close()


    #Get ride wait times from Disney's California Adventure
    index += 1
    waitTimes = f'https://queue-times.com/en-US/parks/{parks[index]}/queue_times.json'
    checkWaitTimes(index, waitTimes)
    f = open(PATH + 'waittimesCaAdventure.json')
    data = json.load(f)
    rides = data['lands']
    createRides(f, rides, rideNames)
    f.close()

    for i in range(len(rideNames)):
        if "'" in rideNames[i].name:
            #Escape apostrophe
            rideNames[i].name = rideNames[i].name.replace("'", "\\'")


    for ride in rideNames:
        print(ride)

    connect_to_db(rideNames)

if __name__ == '__main__':
	main()
