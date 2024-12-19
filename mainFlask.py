import time
from flask import Flask, flash, render_template, request
import joblib
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
import requests
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # This generates a random 32-character string

# Load the trained model
model_filename = 'SmartClock_Env/sleep_quality_model2.pkl'  # Update with full path
model = joblib.load(model_filename)

# Store alarm times (use a list of dictionaries)
user_alarms = []
user_events = []

# Preprocessing pipeline (same as the one used during training)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),  # Handle missing numerical values
            ('scaler', StandardScaler())  # Scale numerical features
        ]), ['Age', 'Physical Activity Level', 'Stress Level']),  # Numerical columns
        
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),  # Fill missing categorical values
            ('encoder', OneHotEncoder(handle_unknown='ignore'))  # One hot encode categorical variable
        ]), ['Gender'])  # Categorical column
    ])

# Generate initial fake data for sleep quality (last 10 days)
dates = [datetime.today() - timedelta(days=i) for i in range(10)]  # Last 10 days
fake_data = {
    'Date': dates,
    'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
    'Age': [25, 30, 22, 40, 28, 35, 30, 28, 33, 25],
    'Physical Activity Level': [50, 60, 40, 30, 55, 45, 65, 40, 60, 70],
    'Stress Level': [5, 6, 4, 5, 3, 7, 6, 4, 5, 6]
}

# Convert to DataFrame
df_fake = pd.DataFrame(fake_data)

# Make predictions using the model for the fake data
input_data = df_fake[['Gender', 'Age', 'Physical Activity Level', 'Stress Level']]
predictions = model.predict(input_data)

# Add the predictions (quality of sleep) to the DataFrame
df_fake['Quality of Sleep'] = predictions

# Save the data (you can save to a CSV or another file format)
df_fake.to_csv('sleep_quality_data.csv', index=False)

# Step 4: Plot the data using Plotly
def generate_plot(dataframe, predicted_value=None):
    fig = px.line(dataframe, x='Date', y='Quality of Sleep', title='Quality of Sleep Over Time',
                  labels={'Date': 'Date', 'Quality of Sleep': 'Quality of Sleep'},
                  line_shape='linear') 

    # Add a marker for the predicted value (if given)
    if predicted_value is not None:
        fig.add_scatter(x=[datetime.today()], y=[predicted_value], mode='markers', name='Predicted Value', marker=dict(color='red', size=12))

    return fig.to_html(full_html=False)

# Store user data temporarily (in a dictionary for simplicity)
user_profile = {
    'name': '',
    'age': '',
    'gender': '',
    'physical_activity': '',
    'stress_level': ''
}

# Weather API Function
def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            weather = {
                "temperature": weather_data["main"]["temp"],
                "condition": weather_data["weather"][0]["description"],
                "temp_min": weather_data["main"]["temp_min"],         # Minimum temperature
                "temp_max": weather_data["main"]["temp_max"]
            }
            return weather
        else:
            return {"error": "Failed to fetch weather data"}
    except Exception as e:
        return {"error": str(e)}
    
# The new functions for calculating wake-up times and setting alarms
def calculate_rem_wake_up_times(bedtime_str, min_cycles=4, max_cycles=6):
    """
    Calculate ideal wake-up times based on reaching REM sleep at the end of each cycle.
    """
    bedtime = datetime.strptime(bedtime_str, "%H:%M")
    cycle_duration = timedelta(minutes=90)
    
    wake_up_times = []
    for cycles in range(min_cycles, max_cycles + 1):
        wake_up_time = bedtime + cycle_duration * cycles
        wake_up_times.append(wake_up_time.strftime("%H:%M"))

    return wake_up_times

def set_alarm(alarm_time):
    """
    Set up an alarm for the chosen wake-up time.
    """
    now = datetime.now()
    alarm_time_today = datetime.strptime(alarm_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    
    # If the alarm time is earlier than the current time, set it for the next day
    if alarm_time_today <= now:
        alarm_time_today += timedelta(days=1)

    print(f"Alarm set for {alarm_time_today.strftime('%Y-%m-%d %H:%M')}.")

    # Calculate the time remaining until the alarm
    sleep_seconds = (alarm_time_today - now).total_seconds()
    print(f"Time remaining until alarm: {int(sleep_seconds // 60)} minutes.")
    
    # Wait until the alarm time
    time.sleep(sleep_seconds)
    
    print("\nALARM! Wake up! ⏰")

def calculate_sleep_duration_in_hours(alarm_time_str):
    """
    Calculate the time remaining until the alarm in hours.
    
    Parameters:
    - alarm_time_str (str): The alarm time in "HH:MM" 24-hour format (e.g., "07:30").
    
    Returns:
    - sleep_duration_hours (int): The duration of sleep in hours.
    """
    # Get the current time
    now = datetime.now()
    
    # Convert the alarm time to a datetime object (same day as the current date)
    alarm_time = datetime.strptime(alarm_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    
    # If the alarm time has already passed today, set it for the next day
    if alarm_time <= now:
        alarm_time += timedelta(days=1)
    
    # Calculate the time remaining until the alarm
    sleep_duration = alarm_time - now
    
    # Convert the sleep duration to hours
    sleep_duration_hours = sleep_duration.total_seconds() // 3600
    
    return int(sleep_duration_hours)

# Example usage:
alarm_time = "07:30"  # Example alarm time in "HH:MM" format
sleep_duration_hours = calculate_sleep_duration_in_hours(alarm_time)
print(f"Time remaining to sleep: {sleep_duration_hours} hours")

# Function to determine the audio based on sleep duration
def get_alarm_audio(sleep_duration_hours):
    if sleep_duration_hours <= 3:
        return "audio/beach_with_birds.mp3"  # First audio for 0-3 hours
    elif 3 < sleep_duration_hours <= 6:
        return "audio/alarm_clock_beeps.mp3"  # Second audio for 3-6 hours
    else:
        return "audio/retro-game-emergency-alarm.mp3"  # Third audio


@app.route('/', methods=['GET', 'POST'])
def home_and_profile():
    global user_profile  # Ensure we are modifying the global user_profile
    global user_alarms  # Ensure we are modifying the global user_alarms
    global user_events  # Ensure we are modifying the global user_events
    predicted_quality = None
    some_condition = True  # This is just an example. Replace with your actual condition.
    another_condition = False  # Replace this with your condition.

    wake_up_times = []  # Initialize as an empty list

    alarm_audio = None  # Initialize alarm audio to None
    messages = []  # Initialize messages list to pass to the frontend

    if some_condition:
        messages.append({"type": "success", "text": "Operation successful!"})
    elif another_condition:
        messages.append({"type": "error", "text": "An error occurred."})

    if request.method == 'POST':
        try:
            if 'bedtime' in request.form:
                bedtime_str = request.form['bedtime']
                try:
                    # Calculate wake-up times based on the provided bedtime
                    wake_up_times = calculate_rem_wake_up_times(bedtime_str)
                    messages.append("Here are your ideal wake-up times based on your bedtime!")
                except ValueError:
                    messages.append("Invalid bedtime format. Please enter in HH:MM format.")

            elif 'selected_alarm' in request.form:
                selected_alarm = request.form['selected_alarm']
                set_alarm(selected_alarm)  # Set the alarm
                messages.append(f"Alarm set for {selected_alarm}.")

                # Calculate sleep duration in hours
                sleep_duration_hours = calculate_sleep_duration_in_hours(selected_alarm)
                messages.append(f"Time remaining to sleep: {sleep_duration_hours} hours")

                alarm_audio = get_alarm_audio(sleep_duration_hours)

            elif 'name' in request.form:
                user_profile['name'] = request.form['name']
                user_profile['age'] = request.form['age']
                user_profile['gender'] = request.form['gender']
                user_profile['physical_activity'] = request.form['physical_activity']
                user_profile['stress_level'] = request.form['stress_level']

            elif 'alarm_time' in request.form:
                alarm_time = request.form['alarm_time']
                # Validate alarm time format (HH:MM)
                if alarm_time and len(alarm_time) == 5 and alarm_time[2] == ':':
                    try:
                        hours, minutes = map(int, alarm_time.split(':'))
                        if 0 <= hours < 24 and 0 <= minutes < 60:
                            user_alarms.append({'time': alarm_time})
                            messages.append(f"Alarm set for {alarm_time}.")
                        else:
                            messages.append("Invalid alarm time. Please enter a valid time between 00:00 and 23:59.")
                    except ValueError:
                        messages.append("Invalid alarm time format. Please enter time in HH:MM format.")
                else:
                    messages.append("Please enter a valid alarm time.")

            elif 'delete_alarm' in request.form:
                alarm_index = int(request.form['delete_alarm'])
                if 0 <= alarm_index < len(user_alarms):
                    user_alarms.pop(alarm_index)

            elif 'event_title' in request.form and 'event_date' in request.form:
                event_title = request.form['event_title']
                event_date = request.form['event_date']
                # Validate event date format (YYYY-MM-DD)
                try:
                    event_date_obj = datetime.strptime(event_date, '%Y-%m-%d')
                    user_events.append({'title': event_title, 'date': event_date_obj})
                    messages.append(f"Event '{event_title}' set for {event_date}.")
                except ValueError:
                    messages.append("Invalid date format. Please use YYYY-MM-DD.")

            elif 'delete_event' in request.form:
                event_index = int(request.form['delete_event'])
                if 0 <= event_index < len(user_events):
                    user_events.pop(event_index)

            # Predict the quality of sleep using the model
            input_data = pd.DataFrame({
                'Gender': [user_profile['gender']],
                'Age': [user_profile['age']],
                'Physical Activity Level': [user_profile['physical_activity']],
                'Stress Level': [user_profile['stress_level']]
            })
            # Ensure all columns with numeric data are actually numeric
            input_data['Age'] = pd.to_numeric(input_data['Age'], errors='coerce')
            input_data['Physical Activity Level'] = pd.to_numeric(input_data['Physical Activity Level'], errors='coerce')
            input_data['Stress Level'] = pd.to_numeric(input_data['Stress Level'], errors='coerce')

            # Fill any NaN values with a default value (e.g., 0 or mean, based on your data)
            input_data = input_data.fillna({
                'Age': input_data['Age'].mean(),
                'Physical Activity Level': input_data['Physical Activity Level'].mean(),
                'Stress Level': input_data['Stress Level'].mean()
            })

            # Predict and handle potential model prediction errors
            try:
                predicted_quality = model.predict(input_data)[0]  # Predict and get the value
            except Exception as e:
                messages.append(f"Error in predicting sleep quality: {str(e)}")

        except Exception as e:
            messages.append(f"An unexpected error occurred: {str(e)}")

    # Weather data
    weather_api_key = '9a7d693979e2b806d6de25cff3c4465c'  # Replace with your API key
    city = 'San Francisco'  # Replace with your city
    weather = get_weather(weather_api_key, city)

    # Generate the Plotly chart from the fake data
    fig_html = generate_plot(df_fake, predicted_quality)
    
    # Render the page with both the profile, predicted result, chart data, and weather data
    return render_template('index.html', messages=messages, alarm_audio=alarm_audio,user_profile=user_profile,wake_up_times=wake_up_times, fig_html=fig_html, prediction=predicted_quality, weather=weather, alarms=user_alarms, events=user_events)


if __name__ == '__main__':
    app.run(debug=True)