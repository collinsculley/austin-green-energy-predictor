# Import dependencies
import pandas as pd
import datetime
from dateutil import tz
import requests
import numpy as np

def convert_DateTime_UTC_to_CST(UTC_datetime_list, list_range):

    CST_datetime_list = []

    for date in list_range:    
        # Convert the date/time to ISO standard in string format
        date_time = datetime.datetime.utcfromtimestamp(UTC_datetime_list[date]).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a datetime object, representing the UTC time
        time_utc = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

        # Replace the timezone field of the datetime object to UTC
        from_zone = tz.gettz('UTC')
        time_utc = time_utc.replace(tzinfo=from_zone)

        # Convert time zone from UTC to central
        to_zone = tz.gettz('America/Chicago')
        time_cst = time_utc.astimezone(to_zone)

        # Append the date/time, year, month, day, and hour
        CST_datetime_list.append({
            "UTC_Time": UTC_datetime_list[date],
            "Date_Time": time_cst.strftime('%Y-%m-%d %H:%M:%S'),
            "Year": time_cst.year,
            "Month":time_cst.month,
            "Day":time_cst.day,
            "Hour":time_cst.hour
            })

    datetimeDataFrame = pd.DataFrame(CST_datetime_list)
    
    return datetimeDataFrame

def calculate_sunhour(sunrise_list, sunset_list, list_range):
   
    sunhour_list = []

    for day in list_range:
        # Convert the date/time to ISO standard in string format
        sunrise_date_time = datetime.datetime.utcfromtimestamp(sunrise_list[day]).strftime('%Y-%m-%d %H:%M:%S')
        sunset_date_time = datetime.datetime.utcfromtimestamp(sunset_list[day]).strftime('%Y-%m-%d %H:%M:%S')

        # Create a datetime object, representing the UTC time
        sunrise_utc = datetime.datetime.strptime(sunrise_date_time, '%Y-%m-%d %H:%M:%S')
        sunset_utc = datetime.datetime.strptime(sunset_date_time, '%Y-%m-%d %H:%M:%S')

        # Replace the timezone field of the datetime object to UTC
        from_zone = tz.gettz('UTC')
        
        sunrise_utc = sunrise_utc.replace(tzinfo=from_zone)
        sunset_utc = sunset_utc.replace(tzinfo=from_zone)

        # Convert time zone from UTC to central
        to_zone = tz.gettz('America/Chicago')
        
        sunrise_cst = sunrise_utc.astimezone(to_zone)
        sunset_cst = sunset_utc.astimezone(to_zone)
        
        # Convert to string
        sunrise_str = sunrise_cst.strftime('%Y-%m-%d %H:%M:%S')
        sunset_str = sunset_cst.strftime('%Y-%m-%d %H:%M:%S')

        # Calculate Sunhour
        sunrise = datetime.datetime.strptime(sunrise_str, '%Y-%m-%d %H:%M:%S')
        sunset = datetime.datetime.strptime(sunset_str, '%Y-%m-%d %H:%M:%S')
        Sunhour_timedelta = sunset - sunrise
        Sunhour_seconds = Sunhour_timedelta.seconds
        Sunhour = Sunhour_seconds / 3600

        # Append to List
        sunhour_list.append({
            "Sunrise": sunrise_list[day],
            "Sunhour": Sunhour
        })
        
    sunhourDataFrame = pd.DataFrame(sunhour_list)
    
    return sunhourDataFrame

def makeAPIRequest(lat, lon, weather_api_key):
    # Request Parameters
    part = "minutely,alerts"
    units = "imperial"
    
    # Make a request to openweathermap
    requestURL = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&units={units}&appid={weather_api_key}"
    
    response = requests.get(requestURL)

    if response.status_code == 200:
        # Turn the response into a JSON object
        responseJson = response.json()
        return responseJson
        # print("Successfully turned response into JSON object.")
    else:
        # Else, print the Error status code
        errorCode = response.status_code
        return print(f"The Error Status Code is: {errorCode}")

def current_solar_weather(responseJson):
    # Convert the json response to a pandas dataframe
    current_weather_DF = pd.DataFrame([{
        "UTC_Time": responseJson["current"]["dt"],
        "Temperature_F": responseJson["current"]["temp"], 
        "Humidity_percent": responseJson["current"]["humidity"],
        "CloudCover_percent": responseJson["current"]["clouds"],
        "uvIndex": responseJson["current"]["uvi"],
        "Sunrise": responseJson["current"]["sunrise"],
        "Weather_Description": responseJson["current"]["weather"][0]["description"]
    }])

    return current_weather_DF

def forecasted_daily_solar(responseJson):
    # Initiate list
    forecasted_daily_weather = []

    # Append json response to list
    for day in np.arange(0, 8, 1):
        try:
            forecasted_daily_weather.append({
                "UTC_Time": responseJson["daily"][day]["dt"],
                "Sunrise": responseJson["daily"][day]["sunrise"],
                "Sunset": responseJson["daily"][day]["sunset"],
                "uvIndex": responseJson["daily"][day]["uvi"]
            })
        except KeyError:
            forecasted_daily_weather.append({
                "UTC_Time": responseJson["daily"][day]["dt"],
                "Sunrise": responseJson["daily"][day]["sunrise"],
                "Sunset": responseJson["daily"][day]["sunset"],
                "uvIndex": 1
            })

    # Convert list to pandas dataframe
    daily_weather_DF = pd.DataFrame(forecasted_daily_weather)
    
    return daily_weather_DF

def forecasted_hourly_solar(responseJson):
    # Initiate list
    forecasted_hourly_weather = []

    # Append json response to list
    for hour in np.arange(0, 48, 1):
        forecasted_hourly_weather.append({
            "UTC_Time": responseJson["hourly"][hour]["dt"],
            "Temperature_F": responseJson["hourly"][hour]["temp"],
            "Weather_Description": responseJson["hourly"][hour]["weather"][0]["description"],
            "CloudCover_percent": responseJson["hourly"][hour]["clouds"],
            "Humidity_percent": responseJson["hourly"][hour]["humidity"]
        })

    # Convert list to pandas dataframe
    hourly_weather_DF = pd.DataFrame(forecasted_hourly_weather)
    
    return hourly_weather_DF

def current_wind_weather(responseJson):
    # Convert the json response to a pandas dataframe
    current_weather_DF = pd.DataFrame([{
        "UTC_Time": responseJson["current"]["dt"],
        "Temperature_F": responseJson["current"]["temp"], 
        "Weather_Description": responseJson["current"]["weather"][0]["description"],
        "Humidity_percent": responseJson["current"]["humidity"],
        "WindSpeed_mph": responseJson["current"]["wind_speed"],
        "WindDirection_degrees": responseJson["current"]["wind_deg"]
    }])

    return current_weather_DF

def forecasted_hourly_wind(responseJson):
    # Initiate list
    forecasted_hourly_weather = []

    # Append json response to list
    for hour in np.arange(0, 48, 1):
        forecasted_hourly_weather.append({
            "UTC_Time": responseJson["hourly"][hour]["dt"],
            "Temperature_F": responseJson["hourly"][hour]["temp"],
            "Weather_Description": responseJson["hourly"][hour]["weather"][0]["description"],
            "Humidity_percent": responseJson["hourly"][hour]["humidity"],
            "WindSpeed_mph": responseJson["hourly"][hour]["wind_speed"],
            "WindDirection_degrees": responseJson["hourly"][hour]["wind_deg"]
        })

    # Convert list to pandas dataframe
    hourly_weather_DF = pd.DataFrame(forecasted_hourly_weather)
    
    return hourly_weather_DF

def modelPrediction(forecasted_weather_df, X_scaled, load_nn):  
    # Predict values for test set
    y_pred = load_nn.predict(X_scaled)
    y_pred = y_pred.ravel()

    # Create dataframe for results
    nn_results = pd.DataFrame()
    nn_results['pred'] = y_pred
    nn_results['Hour'] = forecasted_weather_df['Hour']
    nn_results['Day'] = forecasted_weather_df['Day']
    nn_results['Date_Time'] = forecasted_weather_df['Date_Time']
    
    return nn_results