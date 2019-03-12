import psycopg2
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)
def getConn():
    #function for connecting to the db
    pwFile = open("pw.txt", "r")
    pw = pwFile.read();
    pwFile.close()
    connStr = ("host='cmpstudb-01.cmp.uea.ac.uk' dbname= 'zrt15fsu' user='zrt15fsu' password = " + pw)
    #HOME connection : ("host = 'localhost' dbname = 'studentdb' user ='postgres' password = 'ujj2gk6D'")
    conn = psycopg2.connect(connStr)
    return conn
	
@app.route('/')
def home():
    #default function for home page.
	return render_template('MainPage.html')

#----1st query
@app.route('/addCustomer', methods = ['post'])
def addCustomer():
    #Adding a new customer (1st query)
    #requesting variable from form to replace in query
    custID = request.form['custID']
    name = request.form['name']
    eMail = request.form['email']
    try:
        #establishing a connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        #setting search path to the schema
        cur.execute('SET search_path to public')
        #executing the query
        cur.execute('INSERT INTO Customer VALUES (%s, %s, %s)',[custID, name, eMail])
        conn.commit()
        #returning home page
        return render_template('MainPage.html', NewCust = 'Customer Successfully added')
    #exception in case of error
    except Exception as e:
        return render_template('MainPage.html', NewCust='Unable to add new customer', error = e)
    #close connection 
    finally:
        if conn:
            conn.close()
#----2nd query
@app.route('/createNewTicket', methods = ['post'])
def createNewTicket():
    #Creating new ticket(2nd query)
    #requesting variable from form to replace in query
    ticketID = request.form['ticketID']
    problem = request.form['problem']
    status = request.form['status']
    priority = request.form['priority']
    custID = request.form['CustID']
    prodID = request.form['ProductID']
    try:
        #establishing a connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        #setting search path to the schema
        cur.execute('SET search_path to public')
        #executing the query
        cur.execute('INSERT INTO Ticket VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s) \
        RETURNING ticketID, problem, priority, customerID', \
        [ticketID, problem, status, priority, custID, prodID]) 
        #commiting changes
        conn.commit()
        rows = cur.fetchone()
        #Returning home page with details of the ticket casted as string
        return render_template('Mainpage.html' , confirmTicket = 'Ticket added successfully' + str(rows))
        #Exception in case of an error
    except Exception as e:
        return render_template('Mainpage.html', confirmTicket = 'Unable to create new ticket.',error = e)
    #close connection 
    finally:
        if conn:
            conn.close()
#----3rd query
@app.route('/updateTicket', methods = ['post'])
def updateTicket():
    #requesting variable from form to replace in query
    updateID = request.form['updateID']
    msg = request.form['updateMsg']
    ticketID = request.form['ticketID']
    staffID = request.form['staffID']
    try:
        #establishing a connection 
        conn = None
        conn = getConn()
        cur = conn.cursor()
        #setting search path to the schema
        cur.execute('SET search_path to public')
        #executing the query
        cur.execute('INSERT INTO TicketUpdate VALUES(%s, %s, CURRENT_TIMESTAMP, %s, %s)', [updateID, msg, ticketID, staffID])
        #commiting changes
        conn.commit()
        return render_template('MainPage.html', success = 'Ticket successfully updated')
    except Exception as e:
        return render_template('MainPage.html', success = 'Unable to update ticket.' , error2 = e)
    #close connection 
    finally:
        if conn:
            conn.close()
#----4th query
@app.route('/listOpenTickets', methods = ['get'])
def listOpenTickets():
    try:
        #establishing connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to public')
        #executing query
        cur.execute("SELECT Ticket.TicketID, Problem, Priority,MAX(UpdateTime) FROM Ticket LEFT JOIN TicketUpdate ON ticket.ticketID = ticketupdate.ticketID WHERE Status = 'Open' \
        GROUP BY Ticket.TicketID ORDER BY priority")
        #commiting changes
        conn.commit()
        rows = cur.fetchall()
        return render_template('task4.html', rows = rows)
    #close connection 
    finally:
        if conn:
            conn.close()
#----5th query
@app.route('/closeTicket', methods = ['post'])
def closeTicket():
    #requesting variable from form to replace in query
    ticketID = request.form['ticketID']
    try:
        #Establishing connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to public')
        #Checks the status of the ticket
        cur.execute("SELECT status FROM Ticket WHERE ticketID = %s", [ticketID])
        selectedTicket = cur.fetchone()
        #Checks if ticket is opened or closed. If neither - ticket doesnt exist.
        if selectedTicket[0] == 'Closed':
            #If its closed, return an error.
            return render_template('MainPage.html', successClose = 'Unable to close ticket')
        elif selectedTicket[0] == 'Open' or 'open':
            #else if ticket is open - close it. 
            cur.execute("UPDATE ticket SET Status = 'Closed' WHERE ticketID = %s", [ticketID])
            #commit changes
            conn.commit()
            return render_template('MainPage.html', successClose = "Ticket Successfully Closed")
    except Exception as e:
        return render_template('MainPage.html', successClose = 'Unable to close ticket', errorClose = e)
    #close connection 
    finally:
        if conn:
            conn.close()
#----6th query
@app.route('/listProblem', methods =['post'])
def listProblem():
    #requesting variable from form to replace in query
    ticketID = request.form['ticketID']
    try:
        #Establishing connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to public')
        #executing query
        query1 = cur.execute("Select problem From Ticket Where ticket.ticketID = %s", [ticketID])
        #variable for main problem to be passed into html page
        q1 = cur.fetchone()
        cur.fetchall()
        #executing questiong 6 query
        query2 = cur.execute("SELECT Message, UpdateTime, COALESCE(Staff.Name, Customer.name) \
        FROM Ticket LEFT JOIN TicketUpdate on Ticket.ticketID = TicketUpdate.TicketID LEFT JOIN\
        Staff ON Staff.staffID = ticketupdate.StaffID LEFT JOIN Customer on \
        customer.customerID = ticket.customerID WHERE Ticket.ticketID = %s \
        ORDER BY UpdateTime ASC" , [ticketID])
        rows = cur.fetchall()
        #if any data is returned then proceed to task 6 html page
        if rows:
            return render_template('task6.html', queryData = rows, html = q1[0] )
        #else if no data is returned, then refresh homepage with error
        else:
            return render_template('mainpage.html', problError = 'No data found')
    #exception in case of error
    except Exception as e:
        return render_template('mainpage.html', problError = e)
    #close connection
    finally:
        if conn:
            conn.close()
#----7th query        
@app.route('/produceReport', methods = ['get'])
def produceReport():
    try:
        #Establishing connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to public')
        #executing query
        cur.execute("SELECT Ticket.ticketID, Ticket.Problem , COUNT (TicketupdateID) AS NumOfUpdates, \
        (SELECT (MIN(UpdateTime) - LoggedTime) as FirstResponse), (SELECT (MAX(UpdateTime) - LoggedTime)\
        as LastResponse) FROM Ticket LEFT JOIN TicketUpdate ON \
        Ticket.TicketID = TicketUpdate.TicketID WHERE Status = 'Closed' GROUP BY Ticket.TicketID ORDER BY Ticket.TicketID")
        rows = cur.fetchall()
        #proceed to task 7 html given info from the query
        return render_template('task7.html', queryData = rows)
    #exception in case of error
    except Exception as e:
        return render_template('mainpage.html', produceFail = e)
    #close connection
    finally:
        if conn:
            conn.close()
#----8th query
@app.route('/removeCust', methods = ['post'])
def removeCust():
    #requesting variable from form to replace in query
    custID = request.form['custID']
    try:
        #Establishing connection
        conn = None
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to public')
        #executing query
        cur.execute('DELETE FROM Customer WHERE Customer.CustomerID = %s',[custID])
        #commiting changes
        conn.commit()
        return render_template('mainpage.html', SuccessDelete = 'Customer Successfully Deleted')
    #exception in case of an error
    except Exception as e:
        return render_template('mainpage.html', SuccessDelete = 'Failed to delete customer', FailDelete = e)
    #close connection
    finally:
        if conn:
            conn.close()
if __name__ == '__main__':
    app.run(debug = True)
