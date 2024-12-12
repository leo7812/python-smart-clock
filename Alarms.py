import time
import threading
from tkinter import Tk, Label, Entry, Button, messagebox
from plyer import notification
from datetime import datetime

# Function to display notification
def show_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10  # Display for 10 seconds
        )
    except Exception as e:
        print(f"Notification error: {e}")
    print("Notification displayed successfully.")

# Threaded function to check the alarm
def check_alarm(alarm_time):
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            print("Alarm! Time to wake up!")
            show_notification("Alarm Alert", "Time to wake up!")
            break
        time.sleep(30)  # Wait for 30 seconds before checking again

# Tkinter GUI application
def create_gui():
    # Function to handle setting the alarm from GUI input
    def set_alarm():
        alarm_time = alarm_entry.get()
        if validate_time(alarm_time):
            threading.Thread(target=check_alarm, args=(alarm_time,), daemon=True).start()
            messagebox.showinfo("Alarm Set", f"Alarm set for {alarm_time}")
        else:
            messagebox.showerror("Invalid Time", "Please enter a valid time in HH:MM format.")

    # Validate time format
    def validate_time(alarm_time):
        try:
            time_obj = datetime.strptime(alarm_time, "%H:%M")
            if 0 <= time_obj.hour < 24 and 0 <= time_obj.minute < 60:
                return True
            return False
        except ValueError:
            return False

    # Initialize tkinter window
    root = Tk()
    root.title("Alarm Clock Application")
    root.geometry("300x200")

    # Label and entry for alarm time input
    Label(root, text="Set Alarm (HH:MM):").pack(pady=10)
    alarm_entry = Entry(root, width=10)
    alarm_entry.pack(pady=5)

    # Set Alarm button
    Button(root, text="Set Alarm", command=set_alarm).pack(pady=20)

    root.mainloop()

# Start the tkinter GUI application
if __name__ == "__main__":
    create_gui()
