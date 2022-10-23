# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
unikey = config['DATABASE']['user']
portchoice = config['FLASK']['port']

#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['unikey'] = unikey
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

################################################################################
# Login Page
################################################################################

# This is for the login
# Look at the methods [post, get] that corresponds with form actions etc.
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'unikey' : unikey}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['sid'], request.form['password'])

        # If our database connection gave back an error
        if(val == None):
            flash("""Error with the database connection. Please check your terminal
            and make sure you updated your INI files.""")
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        session['name'] = val[1]
        session['sid'] = request.form['sid']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)


################################################################################
# Logout Endpoint
################################################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))


################################################################################
# List Units page
################################################################################

# List the units of study
@app.route('/list-units')
def list_units():
    # Go into the database file and get the list_units() function
    units = database.list_units()

    # What happens if units are null?
    if (units is None):
        # Set it to an empty list and show error message
        units = []
        flash('Error, there are no units of study')
    page['title'] = 'Units of Study'
    return render_template('units.html', page=page, session=session, units=units)

################################################################################
# Get Locations page
################################################################################

# List of the locations for each lecture
@app.route('/get_locations')
def get_locations():
    # Go into the database file and get the locations() function
    locations = database.get_locations()

    # Say what happens, when locations is null
    if (locations is None):
        # Set it to an empty list and show error message
        units = []
        flash('Error, there are no locations for lectures')
    page['title'] = 'Lecture locations'
    return render_template('locations.html', page=page, session=session, locations=locations)

################################################################################
# Get Classes by room page
################################################################################

@app.route('/get_classesByRoom')
def get_classesByRoom():
    # Go into the database file and get the get_classesByRoom() function
    classCount = database.get_classesByRoom()

    # Say what happens, when classCount is null
    if (classCount is None):
        # Set it to an empty list and show error message
        classCount = []
        flash('Error, there database entries')
    page['title'] = 'Classes By Room'
    return render_template('classesByRoom.html', page=page, session=session, classCount=classCount)

################################################################################
# Get Unit by time page
################################################################################

# Search Unit By Time
@app.route('/get_unitByTime')
def get_unitByTime():
    # Go into the database file and get the get_times() function
    times = database.get_times()
    units = [] 
    # Say what happens, when times is null
    if (times is None):
        # Set it to an empty list and show error message
        times = []
        flash('No Times are available')
    page['title'] = 'Unit by time'
    return render_template('getUnitByTime.html', page=page, session=session, units=units, times = times, default = "--")

# Search Unit By Time - POST
@app.route('/get_unitByTime', methods=['POST'])
def get_unitByTimePost():
    #Get the inserted classtime
    classtime = request.form['classtime']
    times = database.get_times()
    # Go into the database file and get the get_unitByTime function
    units = database.get_unitByTime(classtime)
    # Say what happens, when units is null
    if (units is None):
        # Set it to an empty list and show error message
        units = []
        flash('Please enter a valid time')
    #if (times is None):
    #    times = []
    #    flash('The are no times available')
    page['title'] = 'Unit by time'
    return render_template('getUnitByTime.html', page=page, session=session, units=units, times = times, default = classtime)

################################################################################
# Get insert Lecture Page
################################################################################

# Insert Lecture
@app.route('/insertLecture')
def insertLecture():
    #Set page title
    page['title'] = 'Insert Lecture'
    #Get the get_all_Units() function from the database
    uosList = database.get_All_Units()
    classroomList = database.get_ClassromIDs()
    #Say what happens when uosList is none
    if uosList is None:
        uosList = []
        flash("No units of Study were found")
    else:
        #Split the field
        uosList = list(uosList)
        uosListFinal = []
        for uos in uosList:
            uosListFinal.append(str(uos[0]) + "-" + str(uos[1]) + "-" + str(uos[2]))
    if classroomList is None:
        classroomList = []
        flash("No classrooms were found")
    return render_template('insertLecture.html', page=page, session=session, uosList = uosListFinal, classroomList = classroomList)

# Insert Lecture - POST
@app.route('/insertLecture', methods = ['POST'])
def insertLecturePost():
    uoSCode = request.form['uos'].split("-")[0]
    semester = request.form['uos'].split("-")[1]
    year = request.form['uos'].split("-")[2]
    classTime = request.form['classTime']
    classroomId = request.form['classroomId']
    success = database.insert_lecture(uoSCode, semester, year, classTime, classroomId)
    if (success is None):
        success = ""
        flash('There was an error while inserting - Maybe this combination of uos and classroom has already been inserted')
    else:
        flash('Successfully inserted')
    
    uosList = database.get_All_Units()
    classroomList = database.get_ClassromIDs()
    if uosList is None:
        uosList = []
        flash("No units of Study were found")
    else:
        uosList = list(uosList)
        uosListFinal = []
        for uos in uosList:
            uosListFinal.append(str(uos[0]) + "-" + str(uos[1]) + "-" + str(uos[2]))
    if classroomList is None:
        classroomList = []
        flash("No classrooms were found")
    
    
    page['title'] = 'Insert Lecture'
    return render_template('insertLecture.html', page=page, session=session, uosList = uosListFinal, classroomList = classroomList)

################################################################################
# Get insert Assessment Page
################################################################################

# Insert Assessment
@app.route('/insertAssessment')
def insertAssessment():
    page['title'] = 'Insert Assessment'
    #get the get_UOS_ID() function from the database
    uosList = database.get_UOS_ID()
    assessments = database.get_Assessments()
    #Say what happens when uosList is none
    if uosList is None:
        uosList = []
        flash("No units of Study were found")
    if assessments is None:
        assessment = []
        flash("Error when trying to fetch assessments")
    return render_template('insertAssessment.html', page=page, session=session, uosList = uosList, assessments = assessments)

# Insert Assessment - POST
@app.route('/insertAssessment', methods = ['POST'])
def insertAssessmentPost():
    #Get all the values from the form
    identifier = request.form['id']
    value = request.form['value']
    typ = request.form['type']
    dueDate = request.form['dueDate']
    uoSCode = request.form['uos']
    success = database.insert_Assessment(identifier, value, typ, dueDate, uoSCode)
    #Say what happens when success in None
    if (success is None):
        success = ""
        flash('There was an error while inserting - maybe this id has already been inserted')
    else:
        flash('Successfully inserted')
    #Get the uosList and say what happens when its none
    uosList = database.get_UOS_ID()
    if uosList is None:
        uosList = []
        flash("No units of Study were found")
    
    assessments = database.get_Assessments()
    if assessments is None:
        assessment = []
        flash("Error when trying to fetch assessments")
    page['title'] = 'Insert Assessment'
    return render_template('insertAssessment.html', page=page, session=session, uosList = uosList, assessments = assessments)


