import tkinter as tk
from tkinter import messagebox, filedialog
import json
import subprocess
import tempfile
import os
from datetime import datetime

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
    try:
        # Try to execute a simple command on the device
        result = subprocess.run(['mpremote', 'exec', 'print("connected")'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0 and "connected" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

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
        if not check_device_connection():
            messagebox.showerror("Device Error", 
                "⚠️ No device connected!\n\n"
                "Please connect your device and try again.")
            return
        
        data = collect_sensor_data()
        if data is None:
            return
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file, indent=2)
            temp_filename = temp_file.name
        
        try:
            # Copy file to device using mpremote
            result = subprocess.run(['mpremote', 'cp', temp_filename, ':info.json'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", 
                    "JSON file uploaded to device successfully!\n"
                    "Saved as 'info.json' on the device.")
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
root.title("Sensor Device JSON Generator")
root.geometry("400x480")

# Create import button at the top
import_btn = tk.Button(root, text="Import JSON File", command=import_json_file,
                      bg="lightyellow", font=("Arial", 10, "bold"))
import_btn.grid(row=0, column=0, columnspan=2, pady=10)

# Create and place labels and entry fields
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

# Create buttons
save_computer_btn = tk.Button(root, text="Generate and Save to Computer", 
                             command=generate_and_save_to_computer,
                             bg="lightblue", font=("Arial", 10, "bold"))
save_computer_btn.grid(row=7, column=0, columnspan=2, pady=10)

save_device_btn = tk.Button(root, text="Generate and Save on Device", 
                           command=generate_and_save_to_device,
                           bg="lightgreen", font=("Arial", 10, "bold"))
save_device_btn.grid(row=8, column=0, columnspan=2, pady=5)

# Add some example text to help users
tk.Label(root, text="Example: Latitude: 40.7128, Longitude: -74.0060", 
         font=("Arial", 8), fg="gray").grid(row=9, column=0, columnspan=2, pady=5)

tk.Label(root, text="Note: Device upload requires mpremote tool and connected device", 
         font=("Arial", 8), fg="orange").grid(row=10, column=0, columnspan=2, pady=2)

# Start the GUI event loop
root.mainloop()