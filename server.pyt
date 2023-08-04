from flask import Flask, jsonify, request, session
from flask_cors import CORS
import bcrypt
import psycopg2

db_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'workout'
}

app = Flask(__name__)
CORS(app)

## user
## new user
@app.route ('/user/new', methods=['POST'])
def newUser():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    userData = request.get_json()

    userName = userData.get('username')
    bio = userData.get('bio')
    password= userData.get('password')
    

    if not password:
        return 'password is required', 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    insert_password = hashed_password.decode('utf-8')

    try:
        query = "INSERT INTO users (username, bio, password_digest) VALUES (%s, %s, %s);"
        cursor.execute(query, (userName, bio, insert_password))
        conn.commit()
        return jsonify({'message': "User created successfully"})
    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        print("error seeding user: ", error)
        return "Error creating User", 500
    finally:
        cursor.close()
        conn.close()

## login
from flask import request, jsonify, session
import psycopg2
import bcrypt

@app.route('/user/login', methods=['POST'])
def login():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    verifyData = request.get_json()

    username = verifyData.get('username')
    password = verifyData.get('password')

    try:
        query = "SELECT * from users where username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'message': 'User not found'})
        
        hashed_password = user[3]

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Perform React Native App Auth login here
            # Redirect the user to the authentication endpoint and handle the response

            # Example:
            auth_config = {
                'clientId': 'YOUR_CLIENT_ID',
                'redirectUrl': 'YOUR_REDIRECT_URL',
                'authorizationEndpoint': 'YOUR_AUTHORIZATION_ENDPOINT',
                'scopes': ['YOUR_SCOPES']
            }
            
            # Save the auth configuration to the user's session
            session['auth_config'] = auth_config

            # Return the auth configuration as a response to the React Native app
            return jsonify({'auth_config': auth_config})
        else:
            return jsonify({'message': 'Invalid password'})
    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        print("Error finding user:", error)
        return jsonify({'message': "Could not find user"})
    finally:
        cursor.close()
        conn.close()


## update user
@app.route('/user/update', methods=['PUT'])
def updateUser():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:
        updateUser = request.get_json()

        user_id = updateUser.get('id')
        username = updateUser.get('username')
        bio = updateUser.get('bio')

        cursor.execute("UPDATE users SET username = %s, bio = %s WHERE id = %s",
                   (username, bio, user_id))
        conn.commit()  

        return jsonify({'message': 'User data updated successfully.'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

## userpage
@app.route('/user/<id>', methods=['GET'])
def userpage(id):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = 'select * from users inner join workout on workout.user_id = users.id where users.id = %s;'

    try:
        cursor.execute(query, (id,))
        result = cursor.fetchall()

        user_info = {
            "user_id": result[0][0],
            'username': result[0][1],
            "description": result[0][2]
        }

        workouts = []
        for workout in result:
            workout = {
                "id": workout[4],
                "workout_id": workout[5],
                "title": workout[6],
                "description": workout[7]
            }
            workouts.append(workout)
        
        response = {
            "user_info" : user_info,
            "workouts" : workouts
        }

        return jsonify(response)
    except Exception as e :
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()

##userSearch
@app.route('/user/search', methods=['GET'])
def userSearch():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:
        username = request.args.get('username')
        bio = request.args.get('bio')

        query = "SELECT * FROM users WHERE 1=1"
        params = []

        if username:
            query += " AND username = %s"
            params.append(username)
        if bio:
            query += " AND bio = %s"
            params.append(bio)

     
        cursor.execute(query, params)
        result = cursor.fetchall()

        users = []
        for row in result:
            user = {
                "user_id": row[0],
                "username": row[1],
                "bio": row[2]
            }
            users.append(user)

        response = {
            "users": users
        }

        return jsonify(response)
        return
    except:
        return
    finally:
        cursor.close()
        conn.close()

## workout routes
## returning all
@app.route('/', methods=['GET'])
def homepage():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = "select * from workout inner join users On workout.user_id = users.id"

    try:
        cursor.execute(query)
        workout_data = cursor.fetchall()
        
        workout_list = []
        for workout in workout_data:
            wk = {
                'id': workout[0],
                'title': workout[2],
                'description': workout[3],
                'user_id': workout[4],
                'username': workout[5]
            }
            workout_list.append(wk)
        
        return jsonify(workout_list)
    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        print("Error fetching workout data:", error)
        return jsonify({'message': 'Error fetching workout data'})
    finally:
        cursor.close()
        conn.close()

## individual workout indetification
@app.route('/<id>', methods=['GET'])
def workoutInfo(id):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = 'select * from workout inner join users on workout.user_id = users.id inner join exercise on workout.id = exercise.workout_id where workout.id = %s;'

    try:
        cursor.execute(query, (id,))
        result = cursor.fetchall()

        user_workout_info = {
            'user_id': result[0][1],
            'username': result[0][5],
            'bio': result[0][6],
            'workout_id': result[0][0],
            'workout_title': result[0][2],
            'workout_description': result[0][3]
        }

        exercises = []
        for row in result:
            exercise = {
                'exercise_id': row[8],
                'name': row[10],
                'reps': row[11],
                'sets': row[12],
                'weight': row[13]
            }
            exercises.append(exercise)

        response = {
            'user_workout_info': user_workout_info,
            'exercises': exercises
        }

        return jsonify(response)
    except Exception as e:
        return f"Error excuting query: {str(e)}"
    finally:
        cursor.close()
        conn.close()

## delete 
@app.route('/<id>', methods=['DELETE'])
def deleteWorkout(id):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = 'select * from workout inner join exercise on workout.id = exercise.workout_id where workout.id = %s;'

    try: 
        cursor.execute(query, (id,))
        result = cursor.fetchall()

        if len(result) == 0:
            return jsonify({'message': 'Workout not found'})

        delete_workout_query = 'DELETE FROM workout WHERE id = %s;'
        cursor.execute(delete_workout_query, (id,))
        
        delete_exercises_query = 'DELETE * FROM exercise WHERE workout_id = %s;'
        cursor.execute(delete_exercises_query, (id,))

        conn.commit()

        return jsonify({'message': 'Workout and associated exercises deleted successfully'})    
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

##new 
@app.route('/new', methods=['POST'])
def post():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    postData = request.get_json()

    workout = postData.get('workout')
    exercises = postData.get('exercises')
    user_id = workout.get('user_id')

    try:
        cursor.execute("INSERT INTO workout (user_id, title, description) VALUES (%s, %s, %s) RETURNING id",
                   (user_id, workout['title'], workout['description']))
        workout_id = cursor.fetchone()[0]

        for exercise in exercises:
            cursor.execute("INSERT INTO exercise (workout_id, name, reps, sets, weight) VALUES (%s, %s, %s, %s, %s)",
                       (workout_id, exercise['name'], exercise['reps'], exercise['sets'], exercise['weight']))
            
        conn.commit()

        return jsonify({'message': 'added to db successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

## update
@app.route('/update', methods=['PUT'])
def update():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:
        updateData = request.get_json()

        if 'workout' in updateData:
            workout = updateData['workout']
            workout_id = workout['id']

            cursor.execute("UPDATE workout SET title = %s, description = %s WHERE id = %s",
                       (workout['title'], workout['description'], workout_id))
            conn.commit()  

            return jsonify({'message': 'Workout updated successfully.'}), 200

        elif 'exercise' in updateData:
            exercise = updateData['exercise']
            exercise_id = exercise['id']

            cursor.execute("UPDATE exercise SET name = %s, reps = %s, sets = %s, weight = %s WHERE id = %s",
                       (exercise['name'], exercise['reps'], exercise['sets'], exercise['weight'], exercise_id))
            conn.commit()  

            return jsonify({'message': 'Exercise updated successfully.'}), 200
        
        else: 
            return jsonify({'error': 'Invalid update data'}), 400

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()
        

## get rid of session controller,

if __name__ == '__main__':
    app.run(port=5000)

# @app.route('/user/login', methods=['POST'])
# def login():
#     conn = psycopg2.connect(**db_params)
#     cursor = conn.cursor()

#     verifyData = request.get_json()

#     username = verifyData.get('username')
#     password = verifyData.get('password')

#     try:
#         query = "SELECT * from users where username = %s"
#         cursor.execute(query, (username,))
#         user = cursor.fetchone()

#         if user is None:
#             return jsonify({'message': 'User not found'})
        
#         hashed_password = user[3]

#         if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
#             session['current_user'] = username
#             return jsonify({'message': 'login successful'})
#         else:
#             return jsonify({'messge': 'invalid password'})
#     except(psycopg2.Error, psycopg2.DatabaseError) as error:
#         print("error finding user:", error)
#         return jsonify({'message': "could not find user"})
#     finally:
#         cursor.close()
#         conn.close()