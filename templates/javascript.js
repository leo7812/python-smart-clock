// Get references to HTML elements
const alarmInput = document.getElementById('alarm-time');
const setAlarmButton = document.getElementById('set-alarm');
const clearAlarmButton = document.getElementById('clear-alarm');
const alarmSound = new Audio('alarm_sound.mp3'); // Replace with your sound file

// Function to set an alarm
function setAlarm() {
    const alarmTime = alarmInput.value;
    localStorage.setItem('alarmTime', alarmTime);
    alert('Alarm set for ' + alarmTime);
}

// Function to clear the alarm
function clearAlarm() {
    localStorage.removeItem('alarmTime');
    alert('Alarm cleared');
}

// Function to check the alarm
function checkAlarm() {
    const currentTime = new Date();
    const currentHours = currentTime.getHours().toString().padStart(2, '0');
    const currentMinutes = currentTime.getMinutes().toString().padStart(2, '0');
    const currentFormattedTime = currentHours + ':' + currentMinutes;

    const alarmTime = localStorage.getItem('alarmTime');

    if (alarmTime && currentFormattedTime === alarmTime) {
        alarmSound.play();
        // Optionally, display a notification or alert
        alert('Wake up! Your alarm is ringing.');
        clearAlarm(); // Clear the alarm after it rings
    }
}

// Set an interval to check the alarm every minute
setInterval(checkAlarm, 60000);

// Event listeners for buttons
setAlarmButton.addEventListener('click', setAlarm);
clearAlarmButton.addEventListener('click', clearAlarm);