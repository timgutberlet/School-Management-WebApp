#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['database'],#edit his database in
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# List Units
#   - This function performs a "SELECT" from the database to get the unit
#       of study information.
#   - This is useful for your part when we have to make the page.
################################################################################

def list_units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# List of Lecture Locations
#   - This function performs a "SELECT" from the database to get the locations
#       for lectures information.
################################################################################

def get_locations():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT uosCode, uosName, semester, year, classtime, classroomid
                        FROM UniDB.UnitOfStudy JOIN UniDB.Lecture USING (uosCode)
                        ORDER BY uosCode, semester, year""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# List of Classes by Room
#   - This function performs a "SELECT" from the database to get the Classes grouped by rooms
################################################################################

def get_classesByRoom():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT lecture.classroomID, COUNT(lecture.uoSCode)
                        FROM UniDB.Lecture
                        GROUP BY lecture.classroomid;""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# List of Classes by Room
#   - This function performs a "SELECT" from the database to get the Units for a specific time
################################################################################

def get_unitByTime(classtime = None):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT uoSCode, Semester, year, classTime, classroomId FROM unidb.Lecture WHERE lecture.classtime = %s;""", [classtime])
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Allows to get all available times of lectures, used for the lecture by time selection
################################################################################

def get_times():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT DISTINCT(classTime) FROM unidb.Lecture ORDER BY classTime;""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Allows to insert a new Lecture with the needed given values
################################################################################

def insert_lecture(uoSCode, semester, year, classTime, classroomId):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""INSERT INTO unidb.Lecture (uoSCode, semester, year, classTime, classroomId)
        VALUES (%s, %s, %s, %s, %s);""", [uoSCode, semester, year, classTime, classroomId])
        conn.commit()
        val = "Successful"
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database  " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Allows to insert a new Assesment
################################################################################

def insert_Assessment(identifier, value, typ, dueDate, uosCode):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""INSERT INTO unidb.Assessment (id, value, type, dueDate, uoSCode)
        VALUES (%s, %s, %s, %s, %s);""", [identifier, value, typ, dueDate, uosCode])
        conn.commit()
        val = "Successful"
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database  " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Returns the primary key of all Unit of Study
################################################################################

def get_UOS_ID():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT uoSCode FROM unidb.UnitOfStudy;""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database : " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Returns all columns of all Assessments
################################################################################

def get_Assessments():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT id, value, type, dueDate, uoSCode FROM unidb.Assessment ORDER BY id ASC;""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database : " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val
    
################################################################################
# Returns the primary key of all Unit of Study Offerings
################################################################################

def get_All_Units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uoSCode, Semester, Year FROM unidb.UoSOffering;""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database : " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

    
################################################################################
# Returns all Classroom ID's
################################################################################

def get_ClassromIDs():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute("""SELECT DISTINCT(classroomid) FROM unidb.Classroom;""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database : " + str(e))

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val



#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")

