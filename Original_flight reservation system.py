import mysql.connector as pymysql 
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
# Initialize global variables
con = None
cursor = None
logged_in_user = None

def connection():
    global con, cursor
    try:
        con = pymysql.connect(host="Keshav", user="root", password="Keshav")
        cursor = con.cursor()
        
        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS Flight_Reservations")
        cursor.execute("USE Flight_Reservations")
        
    except pymysql.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to the database: {e}")

def creating_databases_and_tables():
    connection()
    global con, cursor
    
    create_passenger_table_query = """CREATE TABLE IF NOT EXISTS passenger (
                passenger_id INT AUTO_INCREMENT PRIMARY KEY,
                email_id VARCHAR(255) NOT NULL UNIQUE,
                phone_number VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                number_of_times_travel INT DEFAULT 0,
                bank_account VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                gender VARCHAR(10) NOT NULL
            )"""

    create_table_query = """CREATE TABLE IF NOT EXISTS flight (
                flight_number VARCHAR(10) PRIMARY KEY,
                departure VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                departure_date DATE NOT NULL,
                airline VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                seats_available INT DEFAULT 100
            )"""

    create_booking_table_query = """CREATE TABLE IF NOT EXISTS booking (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                passenger_id INT NOT NULL,
                flight_number VARCHAR(10) NOT NULL,
                ticket_type VARCHAR(20) NOT NULL,
                seats_booked INT NOT NULL,
                food VARCHAR(255),
                amount DECIMAL(10, 2),
                tax DECIMAL(10, 2),
                total DECIMAL(10, 2),
                FOREIGN KEY (passenger_id) REFERENCES passenger(passenger_id) ON DELETE CASCADE,
                FOREIGN KEY (flight_number) REFERENCES flight(flight_number) ON DELETE CASCADE
            )"""

    cursor.execute(create_passenger_table_query)
    cursor.execute(create_table_query)
    cursor.execute(create_booking_table_query)
    con.commit()
    con.close()
    
def LOGIN():
    global logged_in_user, cursor, con
    connection()
    email = email_entry.get()
    password = password_entry.get()
    print("Email:", email)  # Add this line for debugging
    print("Password:", password)
    if not email or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return
    cursor.execute(f'SELECT * FROM passenger WHERE email_id = "{email}" AND password = "{password}"')
    user = cursor.fetchone()
    if user:
        logged_in_user = user
        messagebox.showinfo("Success", "Login successful!")
        booking_window(email)
    else:
        messagebox.showerror("Error", "Invalid credentials. Please try again.")
        con.close()
def booking_window(current_user):
    global logged_in_user, window, cursor, con
    global lgge
    connection()
    window.withdraw()
    booking_screen = tk.Toplevel()
    booking_screen.title("BOOKING")
    
    cursor.execute(f'SELECT passenger_id, email_id, name, gender, phone_number, number_of_times_travel FROM passenger WHERE email_id = "{current_user}"')
    user = cursor.fetchone()
    if user:
        passenger_id, email_id, name, gender, phone_number, number_of_times_travel = user
        membership_status = "Regular Member"
        if number_of_times_travel >= 10:
            membership_status = "Golden Member"
        name_label = Label(booking_screen, text=f"Name: {name}")
        email_label = Label(booking_screen, text=f"Email ID: {email_id}")
        gender_label = Label(booking_screen, text=f"Gender: {gender}")
        phone_label = Label(booking_screen, text=f"Phone Number: {phone_number}")
        membership_label = Label(booking_screen, text=f"Membership Status: {membership_status}")
        #getting date from user
        name_label.pack()
        email_label.pack()
        gender_label.pack()
        phone_label.pack()
        membership_label.pack()

    
    else:
        messagebox.showerror("Error", "User not found.")

    con.close()
    # Add a Label and Entry for Date of Departure
    dod_label = Label(booking_screen, text="Date Of Departure [dd-mm-yyyy]")
    dod_label.pack()
    dod_entry = Entry(booking_screen)
    dod_entry.pack()

    def show():
        dod = dod_entry.get()
        show_flight_list(booking_screen,dod)

    def check():
        dod = dod_entry.get()
        lst = dod.split('-')
        for i in range(len(lst)):
            lst[i] = int(lst[i])

        if lst[0] <= 31 and lst[0] > 0:
            if lst[1] >= 1 and lst[1] <= 12:
                if lst[2] == 2023 or lst[2] == 2024:
                    show_flights_button.config(state="normal")
                else:
                    print("Year should be 2023 or 2024")
            else:
                print("Month should be between 1 and 12")
        else:
            print("Date should be between 1 and 31")

    # Create buttons for checking the date and showing flights
    check_date_button = Button(booking_screen, text="Check Date", command=check)
    show_flights_button = Button(booking_screen, text="Show Flights", command=show, state="disabled")

    check_date_button.pack()
    show_flights_button.pack()

    con.close()



def show_flight_list(booking_screen,dod):
    connection()

    cursor.execute("SELECT flight_number, departure, destination, departure_date, airline, price, seats_available FROM flight")
    flights = cursor.fetchall()

    con.close()

    flight_list_window = tk.Toplevel(booking_screen)
    flight_list_window.title("Flight List")

    # Create a Text widget for displaying flight details
    flight_text = tk.Text(flight_list_window, wrap=tk.WORD)
    flight_text.pack(fill=tk.BOTH, expand=True)

    for flight in flights:
        flight_number, departure, destination, departure_date, airline, price, seats_available = flight

        # Construct the flight details string
        flight_info = f"Flight Number: {flight_number}\nDeparture: {departure}\nDestination: {destination}\nDeparture Date: {dod}\nAirline: {airline}\nPrice: {price}\nSeats Available: {seats_available}\n\n"

        # Insert flight details into the Text widget
        flight_text.insert(tk.END, flight_info)

        # Create a "Book" button for each flight
        book_button = Button(
            flight_text,
            text="Book",
            command=lambda f=flight_number: book_flight(logged_in_user, f)
        )
        flight_text.window_create(tk.END, window=book_button)
        flight_text.insert(tk.END, "\n")  # Add a newline after each flight

    # Make the Text widget scrollable
    scroll = tk.Scrollbar(flight_list_window, command=flight_text.yview)
    flight_text.config(yscrollcommand=scroll.set)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)




def book_flight(user, flight_number):
    connection()
    cursor.execute(f'SELECT * FROM flight WHERE flight_number = "{flight_number}"')
    flight = cursor.fetchone()
    print(flight)

    if not flight:
        messagebox.showerror("Error", "Flight not found.")
        con.close()
        return

    _, departure, destination, _, _, price, seats_available,tax = flight

    print(tax)

    if seats_available <= 0:
        messagebox.showerror("Error", "No available seats for this flight.")
        con.close()
        return

    amount = price
        

    messagebox.showinfo("Success", "Booking successful!")

    cursor.execute("""
    INSERT INTO booking (passenger_id, flight_number, ticket_type, seats_booked, amount,tax,total)
    VALUES (%s, %s, %s, %s, %s,%s,%s)""", (user[0], flight_number, "Economy", 1, amount,tax,amount+tax))
    cursor.execute("""
    UPDATE flight
    SET seats_available = seats_available - 1
    WHERE flight_number = %s""", (flight_number,))

    con.commit()
    
        # Print booking details in the IDE

    cursor.execute(f'SELECT booking_id FROM booking order by booking_id desc limit 1')
    flight = cursor.fetchone()
    booking_id=flight[0]
    print("Booking ID:", booking_id)
    print("Passenger ID:", user)
    print("Flight Number:", flight_number)
    print("Ticket Type:", "Economy")
    print("Seats Booked:", 1)
    print("Amount:", amount)
    print("Tax:", tax)
    print("Total:", amount+tax)

    #else:
     #   messagebox.showerror("Error", "Failed to retrieve booking details.")

def reENTER():
    password_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

def SIGNUP():
    global cursor, con
    connection()
    cursor.execute("USE Flight_Reservations")
    print("running")
    query = f'INSERT INTO passenger (email_id, name, password, gender, phone_number) VALUES("{signup_email_entry.get()}","{signup_username_entry.get()}","{signup_password_entry.get()}", "{gender_var.get()}","{phone_entry.get()}")'
    cursor.execute(query)
    print("after execution")
    con.commit()
    con.close()
    print("Values inserted")

def toggle_checkbox():
    print("Checkbox state:", check_var.get())



# Create the main window
window = tk.Tk()
window.attributes("-fullscreen", True)
window.title("FLIGHT RESERVATION SYSTEM")

# Load the background image
bg_image = ImageTk.PhotoImage(Image.open("flight.png"))
bg_label = tk.Label(window, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Create a Notebook for tabs
tab_container = ttk.Notebook(window)

# Create LOGIN and SIGNUP tabs
login_tab = ttk.Frame(tab_container)
signup_tab = ttk.Frame(tab_container)

tab_container.add(login_tab, text="LOGIN")
tab_container.add(signup_tab, text="SIGNUP")
tab_container.pack()

# LOGIN TAB
email_label = Label(login_tab, text="ENTER EMAIL")
password_label = Label(login_tab, text="ENTER PASSWORD")
email_label.grid(row=0, column=0)
password_label.grid(row=1, column=0)
email_entry = Entry(login_tab)
password_entry = Entry(login_tab, show="*")
email_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)
button_login = Button(login_tab, text="LOGIN", command=LOGIN)
button_reset = Button(login_tab, text="RESET", command=reENTER)
button_login.grid(row=4, column=0)
button_reset.grid(row=4, column=1)
check_var = tk.BooleanVar()
checkbox = Checkbutton(login_tab, text="Remember Me", variable=check_var, command=toggle_checkbox)
checkbox.grid(row=3, columnspan=2)

# SIGNUP TAB
phone_label = Label(signup_tab, text="Phone Number")
email_label = Label(signup_tab, text="Email")
signup_username_label = Label(signup_tab, text="Username")
signup_password_label = Label(signup_tab, text="Password")
gender_label = Label(signup_tab, text="Gender")

phone_label.grid(row=0, column=0)
email_label.grid(row=1, column=0)
signup_username_label.grid(row=2, column=0)
signup_password_label.grid(row=3, column=0)
gender_label.grid(row=4, column=0)

phone_entry = Entry(signup_tab)
signup_email_entry = Entry(signup_tab)
signup_username_entry = Entry(signup_tab)
signup_password_entry = Entry(signup_tab, show="*")
phone_entry.grid(row=0, column=1)
signup_email_entry.grid(row=1, column=1)
signup_username_entry.grid(row=2, column=1)
signup_password_entry.grid(row=3, column=1)
gender_var = StringVar()

gender_dropdown = ttk.Combobox(signup_tab, textvariable=gender_var, values=["Male", "Female", "Other"])
gender_dropdown.grid(row=4, column=1)

signup_button = Button(signup_tab, text="SIGNUP", command=SIGNUP)
signup_button.grid(row=5, columnspan=2)

if __name__ == "__main__":
    connection()
    creating_databases_and_tables()
    window.mainloop()
    widow
    
