import folium
import pandas as pd
import FileParsers as fp
import os

#colors for the MAP
RUN_COLOR = '#2696FF'
WALK_COLOR = '#23FC01'
HIKE_COLOR = '#377736'
GOLF_COLOR = '#EF63FF'
KAYAK_COLOR = '#E2B400'
OTHER_COLOR = '#FF0000'
BIKE_COLOR = '#FFA500'
MULTI_COLOR = '#CCCCCC'
SWIM_COLOR = '#5300EB'


# Create the map for each of the workouts to be added to
m = folium.Map(location=[41.9, -97.3], zoom_start=4)

#iterate through the files in the TCX directory
directoryMapMyWalk = '.\\Workouts\\MapMyWalkTCX' 
directoryGarmin = '.\\Workouts\\GarminGPX' 

#FEATURE GROUPS FOR EACH CATIGORY
run = folium.FeatureGroup(name='Runs', show=True).add_to(m)
walk = folium.FeatureGroup(name='Walks', show=True).add_to(m)
hike = folium.FeatureGroup(name='Hikes', show=True).add_to(m)
golf = folium.FeatureGroup(name='Golf Outings', show=True).add_to(m)
other = folium.FeatureGroup(name='General Workout / Other Sports', show=True).add_to(m)
bike = folium.FeatureGroup(name='Bike Rides', show=True).add_to(m)
multi = folium.FeatureGroup(name='Multisport', show=True).add_to(m)
swim = folium.FeatureGroup(name='Outdoor Swims', show=True).add_to(m)
kayak = folium.FeatureGroup(name='Kayaking', show=True).add_to(m)


#hashmap from catigory to activity
activity_types = {
    "Running" : run,
    "Walking" : walk,
    "Hiking" : hike,
    "Golf" : golf,
    "Whitewater_rafting_kayaking" : kayak,
    "Other" : other,
    "Biking" : bike,
    "Multi_sport": multi,
    "Open_water_swimming":swim
}


#GARMIN
count = 0
lifting_count = 0
treadmill_count = 0
for filename in os.listdir(directoryGarmin):

    count = count + 1
    if count % 100 == 0:
        print("Parsing File #",count)

    #empty file from the downloading portion
    if filename == '.not_found':
        continue

    #get the filename
    f = os.path.join(directoryGarmin,filename)

    #use the GPX parser I wrote
    #currWorkout = fp.TCX_Parser(f)
    currWorkout = fp.GPX_Parser(f)

    #workouts with GPS
    if currWorkout.coords != []:
        #color by category
        color = "#000000"
        if currWorkout.workoutCat.capitalize() == 'Running':
            color = RUN_COLOR
        if currWorkout.workoutCat.capitalize() == 'Walking':
            color = WALK_COLOR
        if currWorkout.workoutCat.capitalize() == 'Hiking':
            color = HIKE_COLOR
        if currWorkout.workoutCat.capitalize() == 'Golf':
            color = GOLF_COLOR
        if currWorkout.workoutCat.capitalize() == 'Whitewater_rafting_kayaking':
            color = KAYAK_COLOR
        if currWorkout.workoutCat.capitalize() == 'Other':
            color = OTHER_COLOR
        if currWorkout.workoutCat.capitalize() == 'Biking':
            color = BIKE_COLOR
        if currWorkout.workoutCat.capitalize() == 'Multi_sport':
            color = MULTI_COLOR
        if currWorkout.workoutCat.capitalize() == 'Open_water_swimming':
            color = SWIM_COLOR
        

        #gets the popup
        html = currWorkout.get_df().to_html(classes="table table-striped table-hover table-condensed table-responsive")
        p = folium.map.Tooltip(html)
        
        #Actually adds the GPS Line
        folium.PolyLine(
        locations=currWorkout.coords,
        color=color,
        weight=5,
        tooltip=p
        #tooltip='Cat: ' + str(currWorkout.workoutCat) + '\nTime: ' + str(currWorkout.time) +'\nCalories: ' + str(currWorkout.calories),
    
        ).add_to(m).add_to(activity_types[currWorkout.workoutCat.capitalize()])
    
    #Workouts without GPS
    else:
        if currWorkout.workoutCat.capitalize() == 'Strength_training':
            lifting_count = lifting_count + 1
        if currWorkout.workoutCat.capitalize() == 'Treadmill_running':
            treadmill_count = treadmill_count + 1

        


#DOES THE TCX FILES (From MapMyWalk)
for filename in os.listdir(directoryMapMyWalk):
    #get the filename
    f = os.path.join(directoryMapMyWalk,filename)

    count = count + 1
    if count % 100 == 0:
        print("Parsing File #",count)

    #use the TCX parser I wrote
    #currWorkout = fp.TCX_Parser(f)
    currWorkout = fp.TCX_Parser(f)

    if currWorkout.coords != []:

        #color by category
        color = "#000000"
        if currWorkout.workoutCat.capitalize() == 'Running':
            color = RUN_COLOR
        if currWorkout.workoutCat.capitalize() == 'Walking':
            color = WALK_COLOR
        if currWorkout.workoutCat.capitalize() == 'Hiking':
            color = HIKE_COLOR
        if currWorkout.workoutCat.capitalize() == 'Golf':
            color = GOLF_COLOR
        if currWorkout.workoutCat.capitalize() == 'Whitewater_rafting_kayaking':
            color = KAYAK_COLOR
        if currWorkout.workoutCat.capitalize() == 'Other':
            color = OTHER_COLOR
        if currWorkout.workoutCat.capitalize() == 'Biking':
            color = BIKE_COLOR

        

        #gets the popup
        html = currWorkout.get_df().to_html(classes="table table-striped table-hover table-condensed table-responsive")
        p = folium.map.Tooltip(html)
        
        folium.PolyLine(
            locations=currWorkout.coords,
            color=color,
            weight=5,
            tooltip=p
            #tooltip='Cat: ' + str(currWorkout.workoutCat) + '\nTime: ' + str(currWorkout.time) +'\nCalories: ' + str(currWorkout.calories),
            ).add_to(m).add_to(activity_types[currWorkout.workoutCat.capitalize()])




# show the map
folium.LayerControl().add_to(m)
print("Total Strength Lifts:", lifting_count)
print("Total Treadmill Runs:", treadmill_count)
print('Saving the map....')
m.save('my_map.html')
print('Done!!')
