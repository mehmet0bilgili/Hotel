import sqlite3
from tkinter import *
from tkinter import messagebox, filedialog
import csv

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('hotel_cars.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS car_info (
        car_plate TEXT PRIMARY KEY,
        room_number TEXT,
        telephone_number TEXT
    )
''')
conn.commit()

# Function to preprocess car plate
def preprocess_car_plate(car_plate):
    return car_plate.replace(" ", "").upper()

# Function to validate room number
def validate_room_number(room_number):
    return room_number.isdigit()

# Function to validate telephone number
def validate_telephone_number(telephone_number):
    if telephone_number.startswith('+'):
        return telephone_number[1:].isdigit()
    return telephone_number.isdigit()

# Function to add car info
def add_car_info():
    car_plate = preprocess_car_plate(car_plate_entry.get())
    room_number = room_number_entry.get()
    telephone_number = telephone_number_entry.get()
    
    if not validate_room_number(room_number):
        messagebox.showerror("Error", "Room number must be a number")
        return
    
    if not validate_telephone_number(telephone_number):
        messagebox.showerror("Error", "Telephone number must be a number, optionally starting with + for country code")
        return

    if car_plate and room_number and telephone_number:
        try:
            cursor.execute('INSERT INTO car_info (car_plate, room_number, telephone_number) VALUES (?, ?, ?)',
                           (car_plate, room_number, telephone_number))
            conn.commit()
            car_plate_entry.delete(0, END)
            room_number_entry.delete(0, END)
            telephone_number_entry.delete(0, END)
            messagebox.showinfo("Success", "Car information added successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Car plate already exists")
    else:
        messagebox.showerror("Error", "All fields are required")

# Function to search car info by car plate
def search_car_info():
    car_plate = preprocess_car_plate(search_entry.get())
    cursor.execute('SELECT room_number, telephone_number FROM car_info WHERE car_plate = ?', (car_plate,))
    result = cursor.fetchone()
    if result:
        room_number, telephone_number = result
        result_label.config(text=f'Room Number: {room_number}, Telephone Number: {telephone_number}')
    else:
        result_label.config(text='Car plate not found')

# Function to search car info by room number
def search_by_room_number():
    room_number = room_search_entry.get()
    
    if not room_number.isdigit():
        room_result_label.config(text='Invalid room number. Please enter a valid room number.')
        return
    
    cursor.execute('SELECT car_plate, telephone_number FROM car_info WHERE room_number = ?', (room_number,))
    result = cursor.fetchall()
    if result:
        results_text = "\n".join([f'Car Plate: {car_plate}, Telephone Number: {telephone_number}' for car_plate, telephone_number in result])
        room_result_label.config(text=results_text)
    else:
        room_result_label.config(text='Room number not found')


# Function to delete car info
def delete_car_info(car_plate, list_window):
    cursor.execute('SELECT room_number, telephone_number FROM car_info WHERE car_plate = ?', (car_plate,))
    result = cursor.fetchone()
    if result:
        cursor.execute('DELETE FROM car_info WHERE car_plate = ?', (car_plate,))
        conn.commit()
        refresh_list_window(list_window)
    else:
        messagebox.showerror("Error", "Car plate not found")

# Function to refresh the list window
def refresh_list_window(list_window):
    for widget in list_window.winfo_children():
        widget.destroy()
    cursor.execute('SELECT car_plate, room_number, telephone_number FROM car_info')
    results = cursor.fetchall()
    for index, (car_plate, room_number, telephone_number) in enumerate(results):
        Label(list_window, text=f'{car_plate} - Room: {room_number}, Tel: {telephone_number}').grid(row=index, column=0)
        Button(list_window, text='Delete', command=lambda cp=car_plate: delete_car_info(cp, list_window)).grid(row=index, column=1)

# Function to list all car info
def list_all_car_info():
    global list_window
    if list_window is None or not list_window.winfo_exists():
        list_window = Toplevel(root)
        list_window.title('All Car Plates')
        refresh_list_window(list_window)
    else:
        refresh_list_window(list_window)

# Function to export data to CSV
def export_to_csv():
    cursor.execute('SELECT * FROM car_info')
    rows = cursor.fetchall()
    
    with filedialog.asksaveasfile(mode='w', defaultextension=".csv", filetypes=[("CSV files", "*.csv")]) as file:
        if file:
            writer = csv.writer(file)
            writer.writerow(['Car Plate', 'Room Number', 'Telephone Number'])
            writer.writerows(rows)
            messagebox.showinfo("Success", "Data exported to CSV successfully")

# Set up the main window
root = Tk()
root.title('Car Plate Tracker System')

# Global variable for the list window
list_window = None

# Add car info form
Label(root, text='Car Plate').grid(row=0, column=0)
car_plate_entry = Entry(root)
car_plate_entry.grid(row=0, column=1)

Label(root, text='Room Number').grid(row=1, column=0)
room_number_entry = Entry(root)
room_number_entry.grid(row=1, column=1)

Label(root, text='Telephone Number').grid(row=2, column=0)
telephone_number_entry = Entry(root)
telephone_number_entry.grid(row=2, column=1)

Button(root, text='Add Car Info', command=add_car_info).grid(row=3, column=0, columnspan=2)

# Search car info form
Label(root, text='Search Car Plate').grid(row=4, column=0)
search_entry = Entry(root)
search_entry.grid(row=4, column=1)

Button(root, text='Search', command=search_car_info).grid(row=5, column=0, columnspan=2)

# Result display
result_label = Label(root, text='')
result_label.grid(row=6, column=0, columnspan=2)

# Search by room number form
Label(root, text='Search by Room Number').grid(row=7, column=0)
room_search_entry = Entry(root)
room_search_entry.grid(row=7, column=1)

Button(root, text='Search', command=search_by_room_number).grid(row=8, column=0, columnspan=2)

# Room search result display
room_result_label = Label(root, text='')
room_result_label.grid(row=9, column=0, columnspan=2)

# List all car info button
Button(root, text='List All Car Plates', command=list_all_car_info).grid(row=10, column=0, columnspan=2)

# Add button for export
Button(root, text='Export to CSV', command=export_to_csv).grid(row=11, column=0, columnspan=2)

root.mainloop()

# Close the database connection
conn.close()
