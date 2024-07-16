import re
import pandas as pd
import geopy.distance
import sys
from datetime import datetime

class GarminWorkout:

    workoutCat = None
    source = None
    coords = []
    time = 0.0
    distance = 0.0
    elevation = 0.0

    def __init__(self,source,workoutType,coords,time,distance,elevation):
        self.workoutCat = workoutType
        self.coords = coords

        #time is in seconds so convert into mins and hours 
        if time is not None:
            hrs = time//3600
            mins = (time - hrs*3600)//60
            secs = time % 60
            if hrs > 0:
                if mins < 10:
                    mins = '0' +  str(int(mins))
                else:
                    mins = str(int(mins))
                if secs < 10:
                    secs = '0' + str(int(secs))
                else:
                    secs = str(int(secs))
                self.time = str(int(hrs)) + ":" + mins + ":" + secs
            else:
                if mins < 10:
                    mins = '0' +  str(int(mins))
                else:
                    mins = str(int(mins))
                if secs < 10:
                    secs = '0' + str(int(secs))
                else:
                    secs = str(int(secs))
                self.time = mins + ":" + secs

        
        #distence convert from meters to miles
        if distance != None:
            self.distance = distance * 0.000621
        else:
            #do a calculation to find the distance travelled.
            #this will be done with geopy
            if self.coords != []:
                for i in range(0,len(self.coords)-1):
                    self.distance = self.distance + geopy.distance.geodesic(self.coords[i], self.coords[i+1]).miles



        self.elevation = elevation
        self.source = source


    def get_df(self):
        df = pd.DataFrame(data=[['Source',self.source],['Cat',self.workoutCat.capitalize()],['Time',self.time],['Elevation Gain (Feet)',self.elevation],['Distance (Miles)',self.distance]],columns = ['Name', 'Value'])
        return df

#Takes in a garmin TCX file of a workout
#returns a GarminWorkout object with all of the infromation from it as nessassary
def TCX_Parser(filename,source):
    #open the file
    f = open(filename)
    #iterate through the lines looking for the infromation
    c = []
    Ttime = 0.0
    Tcalories = 0.0
    cat = None
    currLat = None
    currLong = None
    Tdistance = None
    Televation = 0.0
    currElevation = sys.maxsize

    for line in f:
        if "Activity Sport" in line:
            l = re.search('<Activity Sport=\"(\\D*)\"', line)
            cat = l.group(1)
        elif "TotalTimeSeconds" in line:
            l = re.search('<TotalTimeSeconds>([0-9]*.[0-9]*)</TotalTimeSeconds>',line)
            time = l.group(1)
            Ttime = Ttime + float(time)
        elif "Calories" in line:
            l = re.search('<Calories>([0-9]*.[0-9]*)</Calories>',line)
            cals = l.group(1)
            Tcalories = Tcalories + float(cals)
        elif "LatitudeDegrees" in line:
            l = re.search('<LatitudeDegrees>(-[0-9]*.[0-9]*)</LatitudeDegrees>',line)
            a = re.search('<LatitudeDegrees>([0-9]*.[0-9]*)</LatitudeDegrees>',line)
            if l is not None:
                currLat = l.group(1)
            if a is not None:
                currLat = a.group(1)
        elif "LongitudeDegrees" in line:
            l = re.search('<LongitudeDegrees>(-[0-9]*.[0-9]*)</LongitudeDegrees>',line)
            a = re.search('<LongitudeDegrees>([0-9]*.[0-9]*)</LongitudeDegrees>',line)
            if l is not None:
                currLong = l.group(1)
            if a is not None:
                currLong = a.group(1)
            
            c.append([float(currLat),float(currLong)])
            currLat = None
            currLong = None
        elif "Distance" in line:
            if Tdistance == None:
                l = re.search('<DistanceMeters>([0-9]*.[0-9]*)</DistanceMeters>',line)
                if l is not None:
                    d = l.group(1)
                    Tdistance = float(d)
        elif "Altitude" in line:
            l = re.search("<AltitudeMeters>([0-9]*.[0-9]*)</AltitudeMeters>",line)
            if l is not None:
                num = float(l.group(1))
                if num > currElevation:
                    Televation = Televation + (num-currElevation)
                    currElevation = num
                else:
                    currElevation = num



    #convert meters to feet for the elevation(1:3.28084)
    f.close()
    return GarminWorkout(source,cat,c,Ttime,Tdistance,Televation*3.28084)

    

#utalizes the GPX Files instead
#Get the time by subtracting the last time stamp from the first one
#Get the distance by doing a calculation on long and late compared to previous point
#Elevation gain can be done in the same way
def GPX_Parser(filename,source):

    #open the file
    f = open(filename,encoding="utf8")
    c = []
    Tcalories = 0.0
    cat = ''

    Televation = 0.0
    currElevation = sys.maxsize

    timeStart = None
    timeEnd = None

    #go through each line in the file
    for line in f:
        #this is a line with lat and long data
        l = re.search("<type>([a-z]*|[a-z]*_[a-z]*_[a-z]*|[a-z]*_[a-z]*)</type>", line)
        
        if l is not None:
            #then this is for type
            cat = l.group(1)
            continue
        
        l = re.search("<trkpt lat=\"([0-9]*.[0-9]*|-[0-9]*.[0-9]*)\" lon=\"([0-9]*.[0-9]*|-[0-9]*.[0-9]*)\">", line)
        
        #append the coordinates
        if l is not None:
            c.append([float(l.group(1)),float(l.group(2))])
            continue
        
        #for elevation
        l = re.search("<ele>([0-9]*.[0-9]*)</ele>",line)
        if l is not None:
            num = float(l.group(1))
            if num > currElevation:
                Televation = Televation + (num-currElevation)
                currElevation = num
            else:
                currElevation = num

        l = re.search("<time>[0-9]*-[0-9]*-[0-9]*T([0-9]*:[0-9]*:[0-9]*.[0-9]*)Z</time>",line)

        if l is not None:
            if timeStart == None:
                timeStart = l.group(1)
            timeEnd = l.group(1)

    #find the duration
    FMT = '%H:%M:%S.%f'
    tdelta = datetime.strptime(timeEnd, FMT) - datetime.strptime(timeStart, FMT)

    f.close()
    return GarminWorkout(source,cat,c,tdelta.seconds,None,Televation)