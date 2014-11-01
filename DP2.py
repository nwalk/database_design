"""
Design Project 2

AJ Allison
Nathan Walker

"""
import psycopg2
import csv
from time import strftime
import os


class DBConnect():
    """Creates a database connection and a cursor"""
    def __init__(self):
        self.conn = psycopg2.connect("dbname=one user=one host=168.30.240.96 password=g1")
        self.cur = self.conn.cursor()
        self.conn.commit()

    def query(self):
        raise NotImplementedError


class Sql(DBConnect):
    """SQL class that inherits the database connection. This is where
     we have most of our functions and sql statements for the project"""

    def view_status(self, status='in', L1='Available:\nID|Make|Model\n'):
        self.cur.execute("""SELECT id_number, make, model FROM inventory
                            WHERE status = '{}'
                            ORDER BY id_number ASC;""".format(status))
        rows = self.cur.fetchall()
        print(L1)
        for a, b, c in rows:
            print a, b, c

    def customer(self):
        """connects to customer info and prints order number, name,  phone, email, and id number"""
        self.cur.execute("""SELECT order_no, name, phone, email, id_number
                            FROM customer_info
                            ORDER BY order_no ASC;""")
        rows = self.cur.fetchall()
        print("\nOrder#|Name|Phone#|Email|ID\n")
        for a, b, c, d, e in rows:
            print a, b, c, d, e

    def check_out(self, n, p, e, x):
        """collects phone number, email, and the ATV
           id number. Checks out ATV by updating
           the status column from 'in' to 'out'"""
        try:
            self.cur.execute("""SELECT status FROM inventory WHERE id_number = (%s);""", (x,))
            status = self.cur.fetchone()
            if status == ('out',):
                raise AlreadyCheckedOut  # ("ATV currently checked out!")
            self.cur.execute("""SELECT MAX(order_no) FROM customer_info;""")
            o = self.cur.fetchone()
            a = o[0]
            a += 1
            self.conn.commit()
            z = a, n, p, e, x
            sql = """INSERT INTO customer_info (order_no, name, phone, email,
                                                id_number, check_out, check_in)
                     VALUES (%s, %s, %s, %s, %s, now(), now());"""
            self.cur.execute(sql, z)
            self.conn.commit()
            self.cur.execute("""UPDATE inventory SET status = 'out'
                                WHERE id_number = (%s);""", (x,))
            self.conn.commit()
            self.cur.execute("""INSERT INTO detailed(order_no,
                                                    name,
                                                    phone,
                                                    usage_time)
                                VALUES(%s, %s, %s, 0)""", (a, n, p,))
            self.conn.commit()
            print("Item checked out. Order #{}".format(a))
        except AlreadyCheckedOut:
            print("ATV currently checked out!")

    def view_open(self):
        """Selects columns check_out and check_in where there are both equal"""
        self.cur.execute("""SELECT name, phone, id_number, order_no
                            FROM customer_info WHERE check_out = check_in;""")
        self.conn.commit()
        x = self.cur.fetchall()
        print("Name|Phone|ID Number|Order Number")
        for a, b, c, d in x:
            print a, b, c, d

    def check_in(self, order_no, i_d):
        """
        Updates check_in column with timestamp
        Uses the postgres builtin time methods to
        select a time period of 'time checked out'
        Updates the status column in inventory from 'out' to 'in'
        Updates the total column in inventory with
        sum of the 'time checked out' for each ID
        """
        self.cur.execute("""UPDATE customer_info SET check_in = now()
                            WHERE order_no = (%s);""", (order_no,))
        self.conn.commit()
        self.cur.execute("""SELECT check_out FROM customer_info
                            WHERE order_no = (%s);""", (order_no,))
        time_in = self.cur.fetchone()
        self.conn.commit()
        # need exception for TypeError
        self.cur.execute("""SELECT check_in FROM customer_info
                            WHERE order_no = (%s);""", (order_no,))
        time_out = self.cur.fetchone()
        self.conn.commit()
        a = time_out[0]
        b = time_in[0]
        self.cur.execute("""SELECT timestamp %s - timestamp %s;""", (a, b,))
        total = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""UPDATE customer_info SET total_time = (%s)
                            WHERE order_no = %s;""", (total, order_no,))
        self.conn.commit()
        self.cur.execute("""UPDATE inventory SET status = 'in'
                            WHERE id_number = (%s);""", (i_d,))
        self.conn.commit()
        self.cur.execute("""SELECT sum(total_time) FROM customer_info
                            WHERE id_number = %s;""", (i_d,))
        total_2 = self.cur.fetchall()
        self.conn.commit()

        self.cur.execute("""SELECT name FROM customer_info
                            WHERE id_number = %s
                            AND order_no = %s;""",(i_d, order_no,))
        name = self.cur.fetchone()
        self.cur.execute("""SELECT phone FROM customer_info
                            WHERE id_number = %s
                            AND order_no = %s;""",(i_d, order_no,))
        phone = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT sum(total_time) FROM customer_info
                            WHERE name = %s AND phone = %s;""", (name, phone,))
        total_3 = self.cur.fetchall()
        self.conn.commit()

        self.cur.execute("""UPDATE detailed SET usage_time = %s
                            WHERE order_no = %s
                            AND name = %s;""", (total_3, order_no, name,))
        self.conn.commit()
        self.cur.execute("""UPDATE inventory SET total = (%s)
                            WHERE id_number = (%s);""", (total_2, i_d,))
        self.conn.commit()

        # Simplified table
        self.cur.execute("""SELECT MAX(order_no) FROM customer_info;""")
        users = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""SELECT SUM(total_time) FROM customer_info;""")
        time = self.cur.fetchone()
        self.conn.commit()
        self.cur.execute("""UPDATE simplified SET users = %s;""", (users,))
        self.conn.commit()
        self.cur.execute("""UPDATE simplified SET total_time = %s;""", (time,))
        self.conn.commit()
        print("Item successfully checked in!")

    def search_by_make(self, x):
        """Selects from inventory by make"""
        self.cur.execute("""SELECT id_number, make, model, status FROM inventory
                            WHERE make = (%s);""", (x,))
        rows = self.cur.fetchall()
        print("\nID|Make|Model|Status\n")
        for a, b, c, d in rows:
            print a, b, c, d

    def search_by_id(self, x):
        """Selects from inventory by ID"""
        self.cur.execute("""SELECT id_number, make, model, status FROM inventory
                            WHERE id_number = (%s);""", (x,))
        rows = self.cur.fetchall()
        print("\nID|Make|Model|Status\n")
        for a, b, c, d in rows:
            print a, b, c, d

    def createTable(self, x):
        """Creates tables inventory, and customer_info,
           inserts rows of a csv into inventory"""
        self.cur.execute("""CREATE TABLE inventory(id_number integer UNIQUE,
                                                   make varchar,
                                                   model varchar,
                                                   status varchar,
                                                   total varchar
                                                   );"""
                         )
        self.cur.execute("""CREATE TABLE customer_info(order_no SERIAL,
                                                       name varchar(20),
                                                       phone varchar,
                                                       email varchar,
                                                       id_number integer,
                                                       check_out timestamp,
                                                       check_in timestamp,
                                                       total_time interval
                                                       );"""
                         )
        self.cur.execute("""INSERT INTO customer_info(order_no,
                                                      name,
                                                      phone,
                                                      email,
                                                      id_number,
                                                      check_out,
                                                      check_in,
                                                      total_time)
                            VALUES(0, null, null, null, null, null, null, null)"""
                         )
        self.conn.commit()
        self.cur.execute("""CREATE TABLE detailed(order_no integer,
                                                  name varchar,
                                                  phone varchar,
                                                  usage_time varchar
                                                  );"""
                         )

        self.cur.execute("""CREATE TABLE simplified(users varchar,
                                                    total_time varchar
                                                    );"""
                         )

        self.cur.execute("""INSERT INTO simplified VALUES(0, 0)""")
        self.conn.commit()

        # Inserts data from our created csv into our created table
        with open("{}".format(x)) as csvfile:
            inventory_reader = csv.reader(csvfile, delimiter=',')
            for row in inventory_reader:
                insertstatement = """INSERT INTO inventory (id_number, make, model,
                                     status, total) VALUES (%s, %s, %s, %s, %s);"""
                self.cur.execute(insertstatement, row)
        self.conn.commit()

    def add_item(self, id_number, make, model, status='in'):
        """Adds Item to inventory"""
        sql = """INSERT INTO inventory(id_number, make, model, status)
                 VALUES (%s, %s, %s, %s);"""
        a = id_number, make, model, status
        self.cur.execute(sql, a)
        self.conn.commit()

    def remove_item(self, id_number):
        """Removes an item from inventory"""
        self.cur.execute("""DELETE FROM inventory
                            WHERE id_number = (%s);""", (id_number,))
        self.conn.commit()
        print("Item Removed!")

    def dropTable(self):
        """Delets all tables"""
        self.cur.execute("""DROP TABLE simplified""")
        self.cur.execute("""DROP TABLE detailed""")
        self.cur.execute("""DROP TABLE inventory""")
        self.cur.execute("""DROP TABLE customer_info""")
        self.conn.commit()
        print("Tables Dropped!")

    def close_conn(self):
        """Closes the connection"""
        self.cur.close()
        self.conn.close()

    def report(self, x, title, col):
        """Selects rows from tables to be written to a report
           passes variables on to gen_report"""
        self.cur.execute("""SELECT * FROM {}
                            ORDER BY {} ASC;""".format(x, col))
        self.tuples = self.cur.fetchall()
        self.conn.commit()
        x = x.capitalize()
        StatusReports().gen_report(x, self.tuples, title)


class StatusReports:
    """Gets the current working directory and creates
       a folder for the status report folders"""
    def __init__(self):
        self.path = os.getcwd()
        self.date = strftime("%m-%d-%Y")
        try:
            os.mkdir("{}\Status_Reports".format(self.path))
        except WindowsError:
            pass

    def gen_report(self, x, tuples, title):
        """Creates a folder for the report type and
            writes the tuple rows to a text file"""
        try:
            os.mkdir("{}\Status_Reports\{}".format(self.path, x))
        except WindowsError:
            pass
        self.title = open("{}\Status_Reports\{}\{}_{}_Report.txt".format(self.path, x, self.date, x),"w")
        self.title.write("Status report as of {}\n{}\n".format(self.date, title))
        for t in tuples:
            self.line = '\t     |'.join(str(x) for x in t)
            self.title.write(self.line + '\n')
        print("{} Report Created!".format(x))


class AlreadyCheckedOut(Exception):
    pass
