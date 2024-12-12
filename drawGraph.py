
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to create the plot
def plot_line_graph():
    x = [0, 1, 2, 3, 4, 5]
    y = [0, 1, 4, 9, 16, 25]

    fig = Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(111)
    plot.plot(x, y, label='y = x^2', color='b', marker='o')  # Line graph with markers
    plot.set_title("Line Graph Example")
    plot.set_xlabel("X-axis")
    plot.set_ylabel("Y-axis")
    plot.legend()

    # Embed the plot in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)  # A canvas to display the figure
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create the main Tkinter window
window = tk.Tk()
window.title("Tkinter Line Graph Example")
window.geometry("600x500")

# Create a button to display the graph
plot_button = ttk.Button(window, text="Show Line Graph", command=plot_line_graph)
plot_button.pack(pady=20)

# Run the Tkinter event loop
window.mainloop()


