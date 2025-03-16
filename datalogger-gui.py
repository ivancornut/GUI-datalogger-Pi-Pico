import tkinter as tk
from tkinter import filedialog, Listbox, Scrollbar, messagebox
import subprocess
import os
import time

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write("Your data goes here.")
        print(f"Data saved to {file_path}")

def run_command():

    command = "mpremote connect auto run read_sd.py fs ls sd/"  # Replace with your bash command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    # Clear the previous output
    output_listbox.delete(0, tk.END)

    # Insert each line of the output into the listbox
    for line in result.stdout.splitlines():
        output_listbox.insert(tk.END, line.split()[-1])

def save_selected():
    selected_indices = output_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("No Selection", "Please select an item from the list.")
        return

    selected_item = output_listbox.get(selected_indices[0])
    elements = selected_item.split()
    command  = "mpremote run read_sd.py cp "+":sd/"+elements[-1]+" "+elements[-1]
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result)
    #file_path = filedialog.asksaveasfilename(defaultextension=".txt",
    #                                         filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    #if file_path:
    #    with open(file_path, 'w') as file:
    #        file.write(selected_item)
    #    print(f"Selected item saved to {file_path}")

def update_button_text(event):
    selected_indices = output_listbox.curselection()
    if selected_indices:
        selected_item = output_listbox.get(selected_indices[0]).split()[-1]
        save_selected_button.config(text=f"Download '{selected_item}' from device ")
    else:
        save_selected_button.config(text="Download selected item")

def update_time():
    current_time = time.strftime("%H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

def display_device_time():
    current_time = time.strftime('%H:%M:%S')
    time_label_dev.config(text=current_time)
    root.after(3000, hide_time)

def hide_time():
        time_label_dev.config(text="--:--:--")


# Create the main window
root = tk.Tk()
root.title("Pi Pico Datalogger Interface")

# Create a label to display the text "Current Computer Time"
time_title_label = tk.Label(root, text="Current Computer Time:", font=("Helvetica", 16))
time_title_label.pack(pady = (20, 0))

# Create a label to display the current time
time_label = tk.Label(root, font=("Helvetica", 16))
time_label.pack(pady = (5, 5))

# Create a button to update the time
time_button = tk.Button(root, text="Show device Time", command=display_device_time)
time_button.pack(pady = (5, 0))
# Create a label to display the time
time_label_dev = tk.Label(root, text="--:--:--", font=("Helvetica", 16))
time_label_dev.pack(pady = (5, 20))



# Create a button to save the file
save_button = tk.Button(root, text="Save File", command=save_file)
save_button.pack(pady=20)

# Create a button to run the command
run_button = tk.Button(root, text="See Files on datalogger", command=run_command)
run_button.pack(pady=20)

# Create a button to save the selected item
save_selected_button = tk.Button(root, text="Download selected file", command=save_selected)
save_selected_button.pack(pady=20)

# Create a frame for the listbox and scrollbar
frame = tk.Frame(root)
frame.pack(pady=20)

# Create a scrollbar
scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a listbox to display the command output
output_listbox = Listbox(frame, yscrollcommand=scrollbar.set, width=50, height=10,justify = "center")
output_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# Configure the scrollbar
scrollbar.config(command=output_listbox.yview)

# Bind the selection event to update the button text
output_listbox.bind('<<ListboxSelect>>', update_button_text)

# Start the time update loop
update_time()

# Run the application
root.mainloop()