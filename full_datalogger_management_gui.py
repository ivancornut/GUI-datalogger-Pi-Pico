import tkinter as tk
from tkinter import messagebox, filedialog
import json
import subprocess
import tempfile
import os
import re
from datetime import datetime

def update_computer_time():
    """Update the computer time display"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    computer_time_label.config(text=f"Computer Time:\n{current_time}")
    # Schedule next update in 1000ms (1 second)
    root.after(1000, update_computer_time)

def soft_reset_device():
    result = subprocess.run('mpremote soft-reset', capture_output=True, text=True, timeout=10, shell=True)
    if "no device found" in result.stdout:
        print("No device found")
        root.after(1000, soft_reset_device)
    else:
        print("Device soft reset ready to work")

def get_device_time():
    """Get and display the time from the device"""
    result = subprocess.run('mpremote run read_rtc_time.py', 
                          capture_output=True, text=True, timeout=10, shell=True)
    
    if "no device found" in result.stdout:
        device_time_output.config(text="Device Time:\nNo device found")
    elif result.returncode == 0:
        # Extract numbers from the output string
        numbers = re.findall(r'\d+', result.stdout.strip())
        
        if len(numbers) >= 3:
            # Last number = seconds, second to last = minutes, third to last = hours
            seconds = int(numbers[-1])
            minutes = int(numbers[-2])
            hours = int(numbers[-3])
            
            # Format as HH:MM:SS
            formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            device_time_output.config(text=f"Device Time:\n{formatted_time}")
        else:
            # If we can't extract 3 numbers, show raw output
            device_time_output.config(text=f"Device Time:\n{result.stdout.strip()}")
    else:
        device_time_output.config(text=f"Device Time:\n{result.stdout.strip()}")

def get_sd_files():
    """Get list of files on the device SD card"""
    result = subprocess.run('mpremote connect auto run read_sd.py fs ls sd/', 
                          capture_output=True, text=True, timeout=15, shell=True)
    
    if "no device found" in result.stdout:
        sd_files_listbox.delete(0, tk.END)
        sd_files_listbox.insert(0, "No device found")
        download_btn.config(state="disabled")
    elif result.returncode == 0:
        # Parse the file list from stdout
        files = []
        lines = result.stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            #line = line.split()
            #filesize = line[0]
            #line = line[1]
            if line and not line.startswith('ls :') and line != ':sd/':
                # Remove directory prefix if present
                if line.startswith('sd/'):
                    line = line[3:]
                files.append(line)
        
        # Clear and populate the listbox
        sd_files_listbox.delete(0, tk.END)
        if files:
            for file in files:
                sd_files_listbox.insert(tk.END, file)
            download_btn.config(state="normal")
        else:
            sd_files_listbox.insert(0, "No files found on SD card")
            download_btn.config(state="disabled")
    else:
        sd_files_listbox.delete(0, tk.END)
        sd_files_listbox.insert(0, "Error reading SD card")
        download_btn.config(state="disabled")

def download_selected_files():
    """Download selected files from device SD card"""
    selected_indices = sd_files_listbox.curselection()
    
    if not selected_indices:
        messagebox.showwarning("No Selection", "Please select one or more files to download.")
        return
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    downloaded_files = []
    failed_files = []
    
    for index in selected_indices:
        filename = sd_files_listbox.get(index)
        
        # Skip error messages
        if filename in ["No device found", "No files found on SD card", "Error reading SD card"]:
            continue
        print(filename)
        filename = filename.split()[1] # get only the filename and not the size
        try:
            # Download file using mpremote
            result = subprocess.run(f'mpremote run read_sd.py cp :sd/{filename} data/{filename}',capture_output=True, text=True,timeout=30, shell=True)
            
            print(result.stdout)

            if result.returncode == 0:
                downloaded_files.append(filename)
            else:
                failed_files.append(f"{filename}: {result.stdout.strip()}")
                
        except Exception as e:
            print(e)
            failed_files.append(f"{filename}: {str(e)}")
    
    # Show results
    if downloaded_files and not failed_files:
        messagebox.showinfo("Download Complete", 
            f"Successfully downloaded {len(downloaded_files)} file(s) to 'data' directory:\n" + 
            "\n".join(downloaded_files))
    elif downloaded_files and failed_files:
        messagebox.showwarning("Partial Download", 
            f"Downloaded {len(downloaded_files)} file(s):\n" + "\n".join(downloaded_files) + 
            f"\n\nFailed {len(failed_files)} file(s):\n" + "\n".join(failed_files))
    elif failed_files:
        messagebox.showerror("Download Failed", 
            f"Failed to download {len(failed_files)} file(s):\n" + "\n".join(failed_files))

def set_device_time():
    """Set the time on the device"""
    # Run first command: mpremote rtc --set
    result1 = subprocess.run('mpremote rtc --set', 
                           capture_output=True, text=True, timeout=10, shell=True)
    
    if "no device found" in result1.stdout:
        set_time_output.config(text="Set Time Result:\nNo device found")
        return
    elif result1.returncode != 0:
        set_time_output.config(text=f"Set Time Result:\n{result1.stdout.strip()}")
        return
    
    # Run second command: mpremote run set_rtc_time.py
    result2 = subprocess.run('mpremote run set_rtc_time.py', 
                           capture_output=True, text=True, timeout=10, shell=True)
    
    if "no device found" in result2.stdout:
        set_time_output.config(text="Set Time Result:\nNo device found")
    elif result2.returncode == 0:
        set_time_output.config(text="Set Time Result:\nDevice time was set")
    else:
        set_time_output.config(text=f"Set Time Result:\n{result2.stdout.strip()}")

def import_json_file():
    """Import JSON file to prefill input fields"""
    try:
        # Ask user to select JSON file
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Select JSON file to import"
        )
        
        if not filename:
            return
        
        # Read and parse JSON file
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing entries and populate with imported data
        lat_entry.delete(0, tk.END)
        lon_entry.delete(0, tk.END)
        location_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        timestep_entry.delete(0, tk.END)
        
        # Populate fields (skip if value is 9999 or field doesn't exist)
        if data.get("latitude") != 9999 and data.get("latitude") is not None:
            lat_entry.insert(0, str(data["latitude"]))
        
        if data.get("longitude") != 9999 and data.get("longitude") is not None:
            lon_entry.insert(0, str(data["longitude"]))
        
        if data.get("named_location") != "9999" and data.get("named_location") is not None:
            location_entry.insert(0, data["named_location"])
        
        if data.get("device_name") != "9999" and data.get("device_name") is not None:
            name_entry.insert(0, data["device_name"])
        
        if data.get("description") != "9999" and data.get("description") is not None:
            desc_entry.insert(0, data["description"])
        
        if data.get("timestep") != "9999" and data.get("timestep") is not None:
            timestep_entry.insert(0, str(data["timestep"]))
        
        messagebox.showinfo("Import Success", f"JSON data imported successfully from:\n{filename}")
        
    except json.JSONDecodeError:
        messagebox.showerror("Import Error", "Invalid JSON file format!")
    except KeyError as e:
        messagebox.showerror("Import Error", f"Missing expected field in JSON: {e}")
    except Exception as e:
        messagebox.showerror("Import Error", f"Error importing file: {str(e)}")

def collect_sensor_data():
    """Function to collect and validate data from input fields"""
    # Get raw data from all input fields
    lat_value = lat_entry.get().strip()
    lon_value = lon_entry.get().strip()
    location_value = location_entry.get().strip()
    name_value = name_entry.get().strip()
    desc_value = desc_entry.get().strip()
    timestep_value = timestep_entry.get().strip()
    
    # Check for spaces in device name
    if name_value and ' ' in name_value:
        messagebox.showerror("Device Name Error", 
            f"Device name contains spaces: '{name_value}'\n\n"
            "Spaces in device names are not allowed.\n"
            "Please replace spaces with underscores (_).\n\n"
            "Example: 'Temperature Sensor 01' → 'Temperature_Sensor_01'\n\n"
            "Please fix the device name and try again.")
        return None
    
    # Check for missing values and warn user
    missing_fields = []
    if not lat_value:
        missing_fields.append("Latitude")
    if not lon_value:
        missing_fields.append("Longitude")
    if not location_value:
        missing_fields.append("Named Location")
    if not name_value:
        missing_fields.append("Device Name")
    if not desc_value:
        missing_fields.append("Description")
    if not timestep_value:
        missing_fields.append("Timestep")
    
    # If there are missing fields, show warning and ask user
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        proceed = messagebox.askyesno("Missing Values Warning", 
            f"The following fields are empty:\n{missing_list}\n\n"
            "Missing values will be saved as '9999'.\n\n"
            "Do you want to continue generating the JSON file?")
        if not proceed:
            return None
    
    # Process data and replace empty values with 9999
    try:
        data = {
            "latitude": float(lat_value) if lat_value else 9999,
            "longitude": float(lon_value) if lon_value else 9999,
            "named_location": location_value if location_value else "9999",
            "device_name": name_value if name_value else "9999",
            "description": desc_value if desc_value else "9999",
            "timestep": timestep_value if timestep_value else "9999",
            "generated_at": datetime.now().isoformat()
        }
        return data
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for latitude and longitude!")
        return None

def check_device_connection():
    """Check if a device is connected using mpremote"""
    result = subprocess.run('mpremote exec "print(\"connected\")"', 
                          capture_output=True, text=True, timeout=5, shell=True)
    if "no device found" in result.stdout:
        return False
    return result.returncode == 0 and "connected" in result.stdout

def generate_and_save_to_computer():
    """Generate JSON and save to computer"""
    try:
        data = collect_sensor_data()
        if data is None:
            return
        
        # Ask user where to save the file
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save sensor data as..."
        )
        
        if filename:
            # Write JSON data to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", f"JSON file saved successfully!\n{filename}")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def generate_and_save_to_device():
    """Generate JSON and save to device using mpremote"""
    try:
        # Check if device is connected
        #if not check_device_connection():
        #    messagebox.showerror("Device Error", 
        #        "⚠️ No device connected!\n\n"
        #        "Please connect your device and try again.")
        #    return
        
        data = collect_sensor_data()
        if data is None:
            messagebox.showerror("Error", "⚠️ No No imputs!\n\n","Please fill in minimum information")
            return
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file, indent=2)
            temp_filename = temp_file.name
        
        try:
            # Copy file to device using mpremote
            result = subprocess.run(f'mpremote cp "{temp_filename}" :info.json', 
                                  capture_output=True, text=True, timeout=10, shell=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", 
                    "JSON file uploaded to device successfully!\n"
                    "Saved as 'info.json' on the device.")
            elif "no device found" in result2.stdout:
                messagebox.showerror("Error", "⚠️ No device found")
            else:
                messagebox.showerror("Upload Error", 
                    f"Failed to upload to device:\n{result.stderr}")
        
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)
            
    except subprocess.TimeoutExpired:
        messagebox.showerror("Error", "Device communication timeout!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create main window
root = tk.Tk()
root.title("Datalogger management tool")
root.geometry("750x600")

# Create import button at the top left
import_btn = tk.Button(root, text="Import JSON File", command=import_json_file,
                      bg="lightyellow", font=("Arial", 10, "bold"))
import_btn.grid(row=0, column=0, columnspan=2, pady=10, sticky="w", padx=10)

# Create and place labels and entry fields (left side)
tk.Label(root, text="Latitude:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
lat_entry = tk.Entry(root, width=30)
lat_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Longitude:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
lon_entry = tk.Entry(root, width=30)
lon_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Named Location:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
location_entry = tk.Entry(root, width=30)
location_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Device Name:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
name_entry = tk.Entry(root, width=30)
name_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Description:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
desc_entry = tk.Entry(root, width=30)
desc_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Timestep:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
timestep_entry = tk.Entry(root, width=30)
timestep_entry.grid(row=6, column=1, padx=10, pady=5)

# Create buttons (left side)
save_computer_btn = tk.Button(root, text="Generate and Save to Computer", 
                             command=generate_and_save_to_computer,
                             bg="lightblue", font=("Arial", 10, "bold"))
save_computer_btn.grid(row=7, column=0, columnspan=2, pady=10)

save_device_btn = tk.Button(root, text="Generate and Save on Device", 
                           command=generate_and_save_to_device,
                           bg="lightgreen", font=("Arial", 10, "bold"))
save_device_btn.grid(row=8, column=0, columnspan=2, pady=5)

# Add some example text to help users (left side)
tk.Label(root, text="Example: Latitude: 40.7128, Longitude: -74.0060", 
         font=("Arial", 8), fg="gray").grid(row=9, column=0, columnspan=2, pady=5)

tk.Label(root, text="Note: Device upload requires mpremote tool and connected device", 
         font=("Arial", 8), fg="orange").grid(row=10, column=0, columnspan=2, pady=2)

# Add vertical separator
separator = tk.Frame(root, width=2, bg="gray")
separator.grid(row=0, column=2, rowspan=15, sticky="ns", padx=10)

# RIGHT SIDE - Time Management Section
# Computer time display
computer_time_label = tk.Label(root, text="Computer Time:\nLoading...", 
                              font=("Arial", 10, "bold"), justify="center",
                              relief="sunken", bd=2, pady=5)
computer_time_label.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

# Device time section
get_time_btn = tk.Button(root, text="Get Device Time", command=get_device_time,
                        bg="lightcyan", font=("Arial", 9, "bold"))
get_time_btn.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

device_time_output = tk.Label(root, text="Device Time:\nClick button to check", 
                             font=("Arial", 9), justify="center",
                             relief="sunken", bd=1, pady=5, wraplength=150)
device_time_output.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

# Set device time section
set_time_btn = tk.Button(root, text="Set Device Time", command=set_device_time,
                        bg="lightcoral", font=("Arial", 9, "bold"))
set_time_btn.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

set_time_output = tk.Label(root, text="Set Time Result:\nClick button to set time", 
                          font=("Arial", 9), justify="center",
                          relief="sunken", bd=1, pady=5, wraplength=150)
set_time_output.grid(row=4, column=3, padx=10, pady=5, sticky="ew")

# SD Card File Management Section
tk.Label(root, text="SD Card Files", font=("Arial", 10, "bold")).grid(row=5, column=3, padx=10, pady=(15,5))

get_files_btn = tk.Button(root, text="Get SD Card Files", command=get_sd_files,
                         bg="lightsteelblue", font=("Arial", 9, "bold"))
get_files_btn.grid(row=6, column=3, padx=10, pady=5, sticky="ew")

# Listbox for file selection
sd_files_listbox = tk.Listbox(root, height=6, selectmode=tk.MULTIPLE, font=("Arial", 8))
sd_files_listbox.grid(row=7, column=3, padx=10, pady=5, sticky="ew")
sd_files_listbox.insert(0, "Click 'Get SD Card Files' to load")

# Scrollbar for the listbox
scrollbar = tk.Scrollbar(root, orient="vertical")
scrollbar.grid(row=7, column=4, sticky="ns", pady=5)
sd_files_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=sd_files_listbox.yview)

download_btn = tk.Button(root, text="Download Selected Files", command=download_selected_files,
                        bg="lightsalmon", font=("Arial", 9, "bold"), state="disabled")
download_btn.grid(row=8, column=3, padx=10, pady=5, sticky="ew")

# Configure column weights for proper resizing
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=0)  # Scrollbar column

# Start updating computer time
update_computer_time()

# Execute until a device is there to soft reset
soft_reset_device()

# Start the GUI event loop
root.mainloop()
