"""

Design Project 2

AJ Allison
Nathan Walker

"""
import sys, time
from DP2 import Sql


class Menu():
    """Displays a menu and respond to choices when run."""
    def __init__(self):
        self.SQL = Sql()
        self.choices = {
                5: self.search,
                1: self.v_avail,
                2: self.v_checked,
                3: self.c_out,
                4: self.c_in,
                7: self.status_reports,
                9: self.cust,
                10: self.quit,
                11: self.add_data,
                12: self.remove,
                6: self.update_menu,
                8: self.Open
                }

    def display_menu(self):
        print("""
ATV Rentals:
                   MAIN MENU

   |Rental|       |Inventory|     |Customer|

1 View Available  5 - Search    8 - View Current
2 View Checked    6 - Update    9 - View Customers
3 Check out       7 - Status
4 Check in            Reports

10 EXIT

for testing:
11 - Add Table
12 - Drop Tables
""")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{} is not a valid choice".format(choice))

    def search(self):
        """Queries items returning the row in the form of a tuple;
           can search by make, ID number, and status"""
        choice = None
        while choice != '4':
            print("""
                    1 - Search by ATV (make only)
                    2 - Search by ID number
                    3 - Search by Status 'in' or 'out'
                    4 - Back
                """)
            choice = raw_input("Make a choice: ")
            if choice == '1':
                x = raw_input("Enter ATV make:")
                y = self.SQL.search_by_make(x)
                print(y)
            if choice == '2':
                x = raw_input("Enter ID number:")
                y = self.SQL.search_by_id(x)
                print(y)
            if choice == '3':
                x = raw_input("Enter Status in/out:")
                if x == 'in':
                    self.SQL.view_status()
                elif x == 'out':
                    self.SQL.view_status('out', 'Checked Out:\nID|Make|Model\n')()
            if choice == '4':
                self.SQL.close_conn()
                Menu().run()

    def update_menu(self):
        """Menu to update inventory; one can add and remove an item from
        our inventory or go back to main menu"""
        choice = None
        while choice != '3':
            print("""
                    1 - Add ATV to inventory
                    2 - Remove ATV from inventory
                    3 - Back
                """)
            choice = raw_input("Make a choice: ")
            if choice == '1':
                print("please enter the following information: ")
                id_number = raw_input("id_number: ")
                make = raw_input("make: ")
                model = raw_input("model: ")
                confirm = raw_input("""Add this ATV?\nID-{}, Make-{}, Model-{}
Enter y to add, anything else to cancel:""".format(id_number, make, model))
                if confirm == 'y':
                    self.SQL.add_item(id_number, make, model)
                else:
                    self.SQL.close_conn()
                    Menu().run()
            if choice == '2':
                print("Please enter the following information: ")
                id_number = raw_input("ID number: ")
                x = raw_input("""Confirm delete?\nID-{}
Enter y to delete, anything else to cancel:""".format(id_number,))
                if x == 'y':
                    self.SQL.remove_item(id_number)
                else:
                    self.SQL.close_conn()
                    Menu().run()
            if choice == '3':
                self.SQL.close_conn()
                Menu().run()

    def status_reports(self):
        """Menu to generate inventory reports. Either in the form of
        a whole inventory report, a detailed with every item, and a simplified
        for each user and total time an item was checked out"""
        choice = None
        while choice != '4':
            print("""
                    1 - Create Inventory Report
                    2 - Create Detailed Report
                    3 - Create Simplified Report
                    4 - Back
                  """)
            choice = raw_input("Make a choice: ")
            if choice == '1':
                self.SQL.report('inventory', 'ID\t     Make\t     Model\t     Status\t     Usage Time\n','id_number')
            elif choice == '2':
                self.SQL.report('detailed', 'Order Num\t Name\t  Phone\t\t  Usage Time\n', 'order_no')
            elif choice == '3':
                self.SQL.report('simplified', 'Total Users\tTotal Usage Time\n', 'users')
            elif choice == '4':
                self.SQL.close_conn()
                Menu().run()

    def v_avail(self):
        """Returns items that are available for checking out"""
        return self.SQL.view_status()

    def v_checked(self):
        """Returns items that are already checked out"""
        return self.SQL.view_status('out', 'Checked Out:\nID|Make|Model\n')

    def Open(self):
        """Calls our view open function in DP2 file"""
        return self.SQL.view_open()

    def c_out(self):
        while True:
            try:
                x = int(raw_input("ID number:"))
                break
            except ValueError:
                print("Please enter a valid number")
        n = raw_input("Name:")
        while True:
            try:
                p = int(raw_input("Phone:"))
                break
            except ValueError:
                print("Please enter numbers only")
        e = raw_input("email:")
        return self.SQL.check_out(n, p, e, x)

    def c_in(self):
        """Print statements and logic behind the check in function in the DP2 file"""
        print("To check in an ATV please enter the Order/ID number")
        print("Current orders:")
        self.SQL.view_open()
        # a = {}
        while True:
            try:
                y = int(raw_input("ID number:"))
                break
            except ValueError:
                print("Please enter a valid number")
        while True:
            try:
                x = int(raw_input("Order number:"))
                break
            except ValueError:
                print("Please enter a valid number")
        print("Correct Order/ID number? "), x, y
        correct = raw_input("Is this correct? Hit y for submit")
        # a[x] = y
        if correct == 'y':
            self.SQL.check_in(x, y)
        else:
            self.SQL.close_conn()
            Menu().run()
        more = raw_input("Check in another? y/n:")
        if more == 'y':
            self.c_in()
        else:
            self.SQL.close_conn()
            Menu().run()

    def report(self):
        """Function that calls the status reports"""
        self.SQL.stat_report()
        pass

    def cust(self):
        """Function that calls the customer report"""
        return self.SQL.customer()

    def quit(self):
        """Function allows the user to quit the program"""
        print("Thank you, bye...")
        sys.exit(0)

    def add_data(self):
        """Used to add data to our inventory after giving the right file path name
         to the csv"""
        x = raw_input("Enter path with name to CSV\nIE 'C:/Users/Desktop/SomeFile.csv'\nPath:")
        self.SQL.createTable(x)
        print("table created")

    def remove(self):
        """Drops tables"""
        self.SQL.dropTable()
        print("tables deleted")

if __name__ == "__main__":
    Menu().run()
