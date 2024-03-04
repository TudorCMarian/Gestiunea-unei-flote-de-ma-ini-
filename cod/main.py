from flask import Flask, render_template, jsonify, request, redirect
import cx_Oracle
from datetime import datetime

app = Flask(__name__)
print('Connecting to Oracle...')
username = "bd138"
password = "bd138"
dsn = "(DESCRIPTION = (ADDRESS_LIST =(ADDRESS = (PROTOCOL = TCP)(HOST = bd-dc.cs.tuiasi.ro)(PORT = 1539)))(CONNECT_DATA =(SERVICE_NAME = orcl)))"
con = cx_Oracle.connect(username, password, dsn)
print(f'Successfully connected to {username}! Oracle Database version: ', con.version)

# users begin code

@app.route('/')
@app.route('/users')
def Sel_User():
    users=[]
    cur = con.cursor()
    cur.execute('select * from users')
    for result in cur:
        user = {'id': result[0], 'first_name': result[1], 'last_name': result[2], 'email': result[3],
                'birth_date': result[4], 'registration_date': result[5]}
        users.append(user)
    cur.close()
    return render_template('users.html', users=users)


@app.route('/addUser', methods=['GET', 'POST'])
def add_user():
    error = None
    if request.method == 'POST':
        cur = con.cursor()
        cur.execute('select max(id) from users')
        for result in cur:
            id = result[0]
        cur.close()
        if id is None:
            id = 0
        id += 1

        cur = con.cursor()

        values = []
        values.append("'" + str(id) + "'")
        values.append("'" + request.form['first_name'] + "'")
        values.append("'" + request.form['last_name'] + "'")
        values.append("'" + request.form['email'] + "'")
        values.append("'" + datetime.strptime(str(request.form['birth_date']), '%Y-%m-%d').strftime('%d-%b-%y') + "'")
        values.append("'" + datetime.strptime(str(request.form['registration_date']),'%Y-%m-%d').strftime('%d-%b-%y') + "'")

        fields = ['id', 'first_name', 'last_name', 'email', 'birth-date', 'registration_date']
        query = f"INSERT INTO (SELECT id, first_name, last_name, email, birth_date, registration_date FROM users) VALUES ({id},{values[1]}, {values[2]}, {values[3]}, {values[4]}, {values[5]})"

        cur.execute(query)
        cur.execute('commit')
        return redirect('/users')
    else:
        return render_template('addUser.html')

@app.route('/deleteUser', methods=['GET', 'POST'])
def del_user():
    if request.method == 'POST':
        aux = request.form['id']
        print(aux)

        try:
            # Deschide o tranzacție
            con.begin()
            cur = con.cursor()

            # Sterge din user_vehicles
            cur.execute('DELETE FROM user_vehicles WHERE user_id = :user_id', {'user_id': aux})

            # Sterge din users
            cur.execute('DELETE FROM users WHERE id = :user_id', {'user_id': aux})

            # Comite tranzacția
            con.commit()

            return redirect('/users')
        except Exception as e:
            # În caz de eroare, facem rollback la tranzacție
            con.rollback()
            print(f"Eroare: {e}")
            return render_template('error.html', error="Eroare la ștergerea utilizatorului.")
        finally:
            if cur:
                cur.close()

    else:
        return render_template('deleteUser.html')
@app.route('/editUser', methods=['GET', 'POST'])
def edit_user():
    user = 0
    cur = con.cursor()

    id = "'" + request.form['id']+"'"
    cur.execute('select id from users where id =' + id)
    for result in cur:
        user = result[0]
    cur.close()

    first_name = "'" + request.form['first_name'] + "'"
    last_name = "'" + request.form['last_name'] + "'"

    email = "'" + request.form['email'] + "'"
    birth_date = "'" + request.form['birth_date'] + "'"
    registration_date = "'" + request.form['registration_date'] + "'"

    cur = con.cursor()
    query = "UPDATE users SET first_name = %s, last_name = %s, email = %s, birth_date = %s, registration_date = %s WHERE id = %s" % (first_name, last_name, email, birth_date, registration_date,  user)
    cur.execute(query)

    return redirect('/users')

@app.route('/getUser', methods=['POST'])
def get_user():
    user = request.form['id']
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE id =' + user)

    usrs = cur.fetchone()
    id = usrs[0]
    first_name = usrs[1]
    last_name = usrs[2]
    email = usrs[3]
    birth_date = datetime.strptime(str(usrs[4]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
    registration_date = datetime.strptime(str(usrs[5]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')

    cur.close()
    return render_template("editUser.html", id = id, first_name = first_name, last_name = last_name, email = email,
                           birth_date = birth_date, registration_date = registration_date)

# users end code
# -------------------------------------------#

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
#vehicles begin code

@app.route('/vehicles')
def Select_vehicle():
    vehicles = []

    cur = con.cursor()
    cur.execute('SELECT id, vin, license_plate, registration_date, exterior_color, model_id FROM vehicles')
    rows = cur.fetchall()
    for result in rows:
        vehicle = {}
        vehicle['id'] = result[0]
        vehicle['vin'] = result[1]
        vehicle['license_plate'] = result[2]
        vehicle['registration_date'] = result[3]
        vehicle['exterior_color'] = result[4]
        vehicle['model_id'] = result[5]

        # Obține numele modelului pentru vehicul
        cur.execute('SELECT Name FROM models WHERE ID = :model_id', {'model_id': result[5]})
        model_name = cur.fetchone()
        vehicle['name'] = model_name[0] if model_name else None
        vehicles.append(vehicle)
        print(vehicles)
    return render_template('vehicles.html', vehicles=vehicles)


@app.route("/addVehicle", methods=['GET', 'POST'])
def Add_vehicle():
    error = None
    if request.method == 'GET':
        # Obține toate modelele din baza de date
        cur = con.cursor()
        cur.execute('SELECT id, name FROM models')
        rows = cur.fetchall()
        models = []
        for result in rows:
            model = {}
            model['id'] = result[0]
            model['name'] = result[1]
            models.append(model)
        print(models)
        return render_template('addVehicle.html', models=models)
    elif request.method == 'POST':
        veh = 0
        cur = con.cursor()
        cur.execute('select max(id) from vehicles')
        for result in cur:
            veh = result[0]
        cur.close()
        veh += 1


        cur = con.cursor()
        values = []
        values.append("'" + str(veh) + "'")
        values.append("'" + request.form['vin'] + "'")
        values.append("'" + request.form['license_plate'] + "'")
        values.append("'" + request.form['registration_date'] + "'")
        values.append("'" + request.form['exterior_color'] + "'")
        values.append("'" + request.form['model_id'] + "'")
        query1 = f"INSERT INTO vehicles(vin, license_plate, registration_date, exterior_color, model_id)  VALUES ({values[1]},{values[2]},{values[3]}, {values[4]},{values[5]})"
        print(query1)
        cur.execute(query1)
        cur.execute('commit')
        return redirect('/vehicles')
    else:
        model = []
        cur = con.cursor()
        cur.execute('select id from models')
        for result in cur:
            model.append(result[0])
        cur.close()
        return render_template('addVehicle.html')


@app.route('/delVehicle', methods=['GET', 'POST'])
def Delete_Vehicle():
    if request.method == 'POST':
        vehicle_id = request.form['id']

        try:
            # Deschide o tranzacție
            con.begin()
            cur = con.cursor()

            # Șterge din vehicles
            cur.execute('DELETE FROM vehicles WHERE id = :vehicle_id', {'vehicle_id': vehicle_id})

            # Comite tranzacția
            con.commit()

            return redirect('/vehicles')
        except Exception as e:
            # În caz de eroare, facem rollback la tranzacție
            con.rollback()
            print(f"Eroare: {e}")
            return render_template('error.html', error="Eroare la ștergerea vehiculului.")
        finally:
            if cur:
                cur.close()
    else:
        return render_template('vehicles.html')


@app.route('/userVehicles')
def user_vehicles():
    user_vehicles_list = []

    cur = con.cursor()
    cur.execute('SELECT u.id, u.first_name, u.last_name, v.id AS vehicle_id, v.vin, v.license_plate, v.registration_date, v.exterior_color, m.name AS model_name '
                'FROM users u '
                'JOIN user_vehicles uv ON u.id = uv.user_id '
                'JOIN vehicles v ON uv.vehicle_id = v.id '
                'JOIN models m ON v.model_id = m.id')

    for result in cur:
        user_vehicle = {
            'user_id': result[0],
            'first_name': result[1],
            'last_name': result[2],
            'vehicle_id': result[3],
            'vin': result[4],
            'license_plate': result[5],
            'registration_date': result[6],
            'exterior_color': result[7],
            'model_name': result[8]
        }
        user_vehicles_list.append(user_vehicle)

    cur.close()
    return render_template('userVehicles.html', user_vehicles=user_vehicles_list)

@app.route('/addUserVehicle', methods=['GET', 'POST'])
def add_user_vehicle():
    if request.method == 'POST':
        user_id = request.form['user_id']
        vehicle_id = request.form['vehicle_id']

        # Verifică dacă user_id și vehicle_id sunt valide (poți adăuga mai multe verificări aici)

        # Execută query-ul de inserare în User_Vehicles
        cur = con.cursor()
        query = "INSERT INTO User_Vehicles (User_Id, Vehicle_Id) VALUES (:user_id, :vehicle_id)"
        cur.execute(query, {'user_id': user_id, 'vehicle_id': vehicle_id})
        con.commit()
        cur.close()

        return redirect('/userVehicles')

    else:
        # Afisează pagina pentru adăugarea userVehicle
        return render_template('addUserVehicle.html')
# main
if __name__ == '__main__':
    app.run(debug = True)
    con.close()