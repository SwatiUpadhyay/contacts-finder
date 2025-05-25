from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

from flask import session

# Hardcoded login credentials
USERNAME = 'rishabh'
PASSWORD = 'chaudhary123'



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages


# Function to read contacts from CSV
def read_contacts():
    contacts = []
    if not os.path.exists('contacts.csv'):
        with open('contacts.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'number'])
    with open('contacts.csv', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contacts.append(row)
    return contacts


# Function to check if contact already exists
def contact_exists(name):
    contacts = read_contacts()
    for contact in contacts:
        if contact['name'].strip().lower() == name.strip().lower():
            return True
    return False


# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
         return redirect(url_for('login'))
    contacts = read_contacts()
    result = None

    if request.method == 'POST':
        search_name = request.form['name'].strip().lower()
        for contact in contacts:
            if search_name in contact['name'].strip().lower():  # Partial match
                result = contact
                break

    return render_template('index.html', result=result)


# Route to add contact
@app.route('/add', methods=['POST'])
def add_contact():
    if not session.get('logged_in'):
         return redirect(url_for('login'))
    name = request.form['new_name'].strip()
    number = request.form['new_number'].strip()

    if contact_exists(name):
        flash('⚠️ Contact already exists!', 'error')
    else:
        with open('contacts.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, number])
        flash('✅ Contact added successfully!', 'success')

    return redirect(url_for('index'))


        # Route to edit a contact number
@app.route('/edit', methods=['POST'])
def edit_contact():
    if not session.get('logged_in'):
         return redirect(url_for('login'))
    name = request.form['edit_name'].strip().lower()
    new_number = request.form['new_number'].strip()

    updated = False
    contacts = read_contacts()

    # Update number in the list
    for contact in contacts:
        if contact['name'].strip().lower() == name:
            contact['number'] = new_number
            updated = True
            break

    # Overwrite the CSV with updated contacts
    if updated:
        with open('contacts.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'number'])
            writer.writeheader()
            writer.writerows(contacts)
        flash('✅ Contact number updated!', 'success')
    else:
        flash('⚠️ Contact not found!', 'error')

    return redirect(url_for('index'))



           # Route to delete a contact
@app.route('/delete', methods=['POST'])
def delete_contact():
    if not session.get('logged_in'):
         return redirect(url_for('login'))
    name = request.form['delete_name'].strip().lower()

    contacts = read_contacts()
    updated_contacts = [c for c in contacts if c['name'].strip().lower() != name]

    if len(contacts) == len(updated_contacts):
        flash('⚠️ Contact not found to delete!', 'error')
    else:
        with open('contacts.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'number'])
            writer.writeheader()
            writer.writerows(updated_contacts)
        flash('🗑️ Contact deleted successfully!', 'success')

    return redirect(url_for('index'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash('✅ Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('❌ Invalid credentials', 'error')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('👋 Logged out successfully!', 'success')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
