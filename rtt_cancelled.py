import requests, sys, json, datetime, sqlite3

session = requests.session() # create session with requests, to remember api credentials

# Check if arguments provided
if len(sys.argv) < 4:
    print("Not enough arguments provided. When calling the script, please specify API username, API password and station code (eg: bex for bexhill)")
    exit(1)

# Collect info from arguments to script
user = sys.argv[1]
password = sys.argv[2]
station = sys.argv[3]
session.auth = (user, password)

# Check if credentials valid
if (session.get("https://api.rtt.io/api/v1/json/search/").status_code == 401):
    print("Unauthorised, please use real API credentials from https://api.rtt.io")
    exit(1)

# Write specified data to DB
def write_cancellations(cancelled, running, late, total, date, hour):
    con = sqlite3.connect("cancelcount.db") # Connect to DB
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS servicecount(cancelled, running, late, total, date, hour, station)") # Create the table

    servicedata = (cancelled, running, late, total, date, hour, station) # data to use for sql query

    # Check if data already exists for hour, if so update data and if not create entry for hour
    exists = cur.execute("SELECT * FROM servicecount WHERE date=? AND hour=? AND station=?", (date, hour, station))
    if exists.fetchone() is None:
        cur.execute("INSERT INTO  servicecount VALUES (?, ?, ?, ?, ?, ?, ?)", servicedata)
    else:
        cur.execute("UPDATE servicecount SET cancelled=?, running=?, late=?, total=? WHERE date=? AND hour=? AND station=?", servicedata)

    con.commit()
    con.close()

# Fetch all data for a specified date
def fetch_db_data_day(date):
    con = sqlite3.connect("cancelcount.db")
    cur = con.cursor()
    data = cur.execute("SELECT cancelled, running, late, total FROM servicecount WHERE date=? AND station=?", (date,station)).fetchall()
    con.close()
    return data


# Fetch data for a specified hour
def fetchForHour(date_time):
    # Fetch data from RealTimeTrains API
    response = session.get("https://api.rtt.io/api/v1/json/search/" + station + "/" + str(date_time.year) + "/" + str(date_time.month).zfill(2) + "/" + str(date_time.day).zfill(2) + "/" + str(date_time.hour).zfill(2) + "00")

    lineup = json.loads(response.content.decode('ascii')) # Load data into python JSON
    
    if type(lineup["services"]) == None.__class__: # If no services are running, return zeroes
        return 0, 0, 0

    # Count the on time, late and cancelled trains for the specified hour
    runningcount = 0
    cancelledcount = 0
    latecount = 0
    totalcount = 0
    for service in lineup["services"]:
        if str(service["locationDetail"]["gbttBookedDeparture"])[0:2] == str(date_time.hour):
            if service["isPassenger"]:  
                if service["locationDetail"]["displayAs"] == "CALL" or service["locationDetail"]["displayAs"] == "ORIGIN":
                    runningcount += 1
                elif (int(service["locationDetail"]["realtimeDeparture"]) - int(service["locationDetail"]["gbttBookedDeparture"]) >= 2):
                    latecount += 1
                if service["locationDetail"]["displayAs"] == "CANCELLED_CALL":
                    cancelledcount += 1
                totalcount += 1
    return cancelledcount, runningcount, latecount, totalcount


now = datetime.datetime.now() # Current time
nexthour = now+datetime.timedelta(hours=1) # Calculate date and time 1 hour from now

datacurrenthour = fetchForHour(datetime.datetime(now.year, now.month, now.day, now.hour)) # fetch for current hour
datanexthour = fetchForHour(datetime.datetime(nexthour.year, nexthour.month, nexthour.day, nexthour.hour)) # fetch for next hour

write_cancellations(datacurrenthour[0], datacurrenthour[1], datacurrenthour[2], datacurrenthour[3], now.date(), now.hour) # Write to DB for current hour
write_cancellations(datanexthour[0], datanexthour[1], datanexthour[2], datacurrenthour[3], nexthour.date(), nexthour.hour) # Write to DB for next hour

# Fetch data for the day from DB and count cancelled, running, late and total for the day so far.
daydata = fetch_db_data_day(now.date())
cancelledday = 0
runningday = 0
lateday = 0
totalday = 0
for hour in daydata:
    cancelledday+=hour[0]
    runningday+=hour[1]
    lateday+=hour[2]
    totalday+=hour[3]

# Return results in logfmt format
print("cancelledtoday="+ str(cancelledday), "ontimetoday=" + str(runningday), "latetoday=" + str(lateday), "totaltoday=" + str(totalday))