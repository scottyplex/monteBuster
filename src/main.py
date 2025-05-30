# src/main.py
import datetime
import json

# --- Data Structures ---

# Pay Period Data Structure:
# Each pay period will be a dictionary with the following keys:
# {
#     'pay_date': datetime.date,  # The actual date the paycheck is received
#     'net_pay': float,           # The net amount of the paycheck
#     'initial_balance': float,   # The starting balance for this period (useful if carrying over a buffer)
#     'assigned_bills': [],       # A list to hold dictionaries of bills assigned to this paycheck
#     'remaining_balance': float  # The balance after all assigned bills are paid
# }

# Bill Data Structure:
# Each bill will be a dictionary with the following keys:
# {
#     'name': str,                # Name of the bill (e.g., 'Rent', 'Electricity')
#     'due_date': datetime.date,  # The date the bill is due
#     'amount': float,            # The amount of the bill
#     'category': str,            # Category (e.g., 'Housing', 'Utilities', 'Food')
#     'paid_by_paycheck_date': datetime.date or None # To link it back to the paycheck that covers it
# }

# ... (Your existing data structure comments here) ...

# --- Core Functions ---

def get_user_pay_info():
    """
    Prompts the user for their last pay date, pay frequency, and net pay.
    Returns a dictionary with this information.
    """
    while True:
        last_pay_date_str = input("Enter your last pay date (YYYY-MM-DD): ")
        try:
            # Convert string to a datetime.date object
            last_pay_date = datetime.datetime.strptime(last_pay_date_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        pay_frequency = input("Enter your pay frequency (bi-weekly or semi-monthly): ").lower().strip()
        if pay_frequency in ["bi-weekly", "semi-monthly"]:
            break
        else:
            print("Invalid pay frequency. Please enter 'bi-weekly' or 'semi-monthly'.")

    while True:
        net_pay_str = input("Enter your net pay amount (e.g., 1500.00): $")
        try:
            net_pay = float(net_pay_str)
            if net_pay <= 0:
                print("Net pay must be a positive number.")
            else:
                break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    return {
        "last_pay_date": last_pay_date,
        "pay_frequency": pay_frequency,
        "net_pay": net_pay
    }

def generate_pay_periods(pay_info):
    """
    Generates a list of pay periods based on user's pay information.
    Each pay period includes pay_date, net_pay, and initial/remaining balances.
    """
    pay_periods = []
    last_pay_date = pay_info["last_pay_date"]
    net_pay = pay_info["net_pay"]
    pay_frequency = pay_info["pay_frequency"]

    # Calculate pay periods until the end of December 2025
    end_date = datetime.date(2025, 12, 31)

    current_pay_date = last_pay_date

    # Generate the first paycheck if it's after the last pay date and within range
    # Or if the last pay date was actually current/future in relation to now
    if current_pay_date > datetime.date.today() or \
       (current_pay_date <= datetime.date.today() and last_pay_date == current_pay_date):
        if current_pay_date <= end_date:
            pay_periods.append({
                'pay_date': current_pay_date,
                'net_pay': net_pay,
                'initial_balance': net_pay,
                'assigned_bills': [],
                'remaining_balance': net_pay
            })

    # Generate subsequent paychecks
    while current_pay_date <= end_date:
        if pay_frequency == "bi-weekly":
            current_pay_date += datetime.timedelta(days=14)
        elif pay_frequency == "semi-monthly":
            # Semi-monthly logic: handles 15th and end of month
            if current_pay_date.day < 15:
                current_pay_date = current_pay_date.replace(day=15)
            elif current_pay_date.day < 28: # Assumes it's the 15th now, next is end of month
                # Go to end of current month
                next_month = current_pay_date.month + 1
                next_year = current_pay_date.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                current_pay_date = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)
            else: # Assumes it's end of month now, next is 15th of next month
                # Go to 15th of next month
                next_month = current_pay_date.month + 1
                next_year = current_pay_date.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                current_pay_date = datetime.date(next_year, next_month, 15)

        if current_pay_date <= end_date:
            pay_periods.append({
                'pay_date': current_pay_date,
                'net_pay': net_pay,
                'initial_balance': net_pay,
                'assigned_bills': [],
                'remaining_balance': net_pay
            })

    return pay_periods

def add_bill():
    """
    Prompts the user for details of a single bill.
    Returns a dictionary representing the bill.
    """
    name = input("Enter bill name (e.g., Rent, Electricity): ").strip()
    while not name:
        print("Bill name cannot be empty.")
        name = input("Enter bill name: ").strip()

    while True:
        due_date_str = input(f"Enter due date for {name} (YYYY-MM-DD): ")
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        amount_str = input(f"Enter amount for {name} (e.g., 500.00): $")
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Amount must be a positive number.")
            else:
                break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    category = input(f"Enter category for {name} (e.g., Housing, Utilities): ").strip()
    if not category:
        category = "Uncategorized" # Default category if none is provided

    return {
        'name': name,
        'due_date': due_date,
        'amount': amount,
        'category': category,
        'paid_by_paycheck_date': None # Will be set during assignment
    }
def get_user_bills():
    """
    Allows the user to repeatedly add bills until they indicate they are done.
    Returns a list of bill dictionaries.
    """
    bills = []
    while True:
        choice = input("\nDo you want to add a bill? (yes/no): ").lower().strip()
        if choice == "yes":
            bill = add_bill()
            bills.append(bill)
        elif choice == "no":
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
    return bills

def save_bills(bills, filename="data/bills.json"):
    """
    Saves a list of bill dictionaries to a JSON file.
    Converts datetime.date objects to strings for JSON serialization.
    """
    # Prepare bills for JSON serialization: convert date objects to strings
    serializable_bills = []
    for bill in bills:
        temp_bill = bill.copy()
        if isinstance(temp_bill['due_date'], datetime.date):
            temp_bill['due_date'] = temp_bill['due_date'].strftime("%Y-%m-%d")
        if temp_bill['paid_by_paycheck_date'] and isinstance(temp_bill['paid_by_paycheck_date'], datetime.date):
            temp_bill['paid_by_paycheck_date'] = temp_bill['paid_by_paycheck_date'].strftime("%Y-%m-%d")
        serializable_bills.append(temp_bill)

    try:
        with open(filename, 'w') as f:
            json.dump(serializable_bills, f, indent=4)
        print(f"Bills saved to {filename}")
    except IOError as e:
        print(f"Error saving bills to {filename}: {e}")

def load_bills(filename="data/bills.json"):
    """
    Loads a list of bill dictionaries from a JSON file.
    Converts date strings back to datetime.date objects.
    """
    bills = []
    try:
        with open(filename, 'r') as f:
            loaded_bills = json.load(f)
        # Convert date strings back to datetime.date objects
        for bill_data in loaded_bills:
            if 'due_date' in bill_data and isinstance(bill_data['due_date'], str):
                bill_data['due_date'] = datetime.datetime.strptime(bill_data['due_date'], "%Y-%m-%d").date()
            if 'paid_by_paycheck_date' in bill_data and isinstance(bill_data['paid_by_paycheck_date'], str):
                bill_data['paid_by_paycheck_date'] = datetime.datetime.strptime(bill_data['paid_by_paycheck_date'], "%Y-%m-%d").date()
            elif bill_data['paid_by_paycheck_date'] == None: # Handle None if it was saved as string "null"
                 bill_data['paid_by_paycheck_date'] = None
            bills.append(bill_data)
        print(f"Bills loaded from {filename}")
    except FileNotFoundError:
        print(f"No existing bill file found at {filename}. Starting with no bills.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}: {e}. Starting with no bills.")
    except Exception as e: # Catch other potential errors during loading
        print(f"An unexpected error occurred while loading bills: {e}. Starting with no bills.")
    return bills

# src/main.py (continued)

# ... (Your existing imports, data structures, get_user_pay_info, generate_pay_periods,
#      add_bill, get_user_bills, save_bills, load_bills functions here) ...

def assign_bills_to_paychecks(pay_periods, bills):
    """
    Assigns bills to the earliest possible paycheck based on their due date,
    ensuring a bill is only assigned if its due date is on or before the paycheck date.
    Prioritizes earlier due dates.
    """
    # Sort bills by due date to ensure earlier bills are paid first
    # Using a lambda function as the key for sorting
    bills.sort(key=lambda bill: bill['due_date'])

    # Make a copy of pay_periods to work with, as we'll modify remaining_balance
    # and assigned_bills for each period
    assigned_pay_periods = [p.copy() for p in pay_periods] # Create shallow copies of periods
    for pp in assigned_pay_periods:
        pp['assigned_bills'] = [] # Ensure this is a new empty list for each copy
        pp['remaining_balance'] = pp['net_pay'] # Reset for fresh assignment

    unassigned_bills = []

    for bill in bills:
        assigned = False
        for pay_period in assigned_pay_periods:
            # Check if bill due date is on or before pay period date AND
            # if the paycheck has enough funds remaining
            if bill['due_date'] <= pay_period['pay_date'] and \
               pay_period['remaining_balance'] >= bill['amount']:
                
                # Assign the bill to this pay period
                pay_period['assigned_bills'].append(bill)
                pay_period['remaining_balance'] -= bill['amount']
                bill['paid_by_paycheck_date'] = pay_period['pay_date'] # Link bill to its paying paycheck
                assigned = True
                break # Move to the next bill once this one is assigned
        
        if not assigned:
            unassigned_bills.append(bill)

    return assigned_pay_periods, unassigned_bills

# src/main.py (continued)

# ... (Your existing imports, data structures, and other functions here) ...

def display_paycheck_summary(pay_periods, unassigned_bills):
    """
    Displays a comprehensive summary of each pay period, including assigned bills
    and remaining balances, and lists any unassigned bills.
    """
    print("\n" + "="*50)
    print("           MONTE BUSTER: FINANCIAL OVERVIEW")
    print("="*50)

    for pp in pay_periods:
        print(f"\n--- Paycheck Date: {pp['pay_date'].strftime('%Y-%m-%d')} ---")
        print(f"  Net Pay: ${pp['net_pay']:.2f}")
        print(f"  Initial Balance for Period: ${pp['net_pay']:.2f}") # Initial from net pay

        if pp['assigned_bills']:
            print("  Assigned Bills:")
            for bill in pp['assigned_bills']:
                print(f"    - {bill['name']:<20} (Due: {bill['due_date'].strftime('%m-%d')}) - ${bill['amount']:.2f}")
        else:
            print("  No bills assigned to this paycheck.")

        print(f"  **Remaining Balance: ${pp['remaining_balance']:.2f}**")
        print("-" * 30) # Separator for each paycheck

    if unassigned_bills:
        print("\n" + "="*50)
        print("          UNASSIGNED BILLS (Insufficient Funds/Past Due)")
        print("="*50)
        for bill in unassigned_bills:
            print(f"  - {bill['name']:<20} (Due: {bill['due_date'].strftime('%Y-%m-%d')}) - ${bill['amount']:.2f} (Cannot be covered by future paychecks)")
    else:
        print("\nAll bills successfully assigned!")

    print("\n" + "="*50)
    print("                 END OF OVERVIEW")
    print("="*50)

# src/main.py (updated main block)

# src/main.py (updated main block)

if __name__ == "__main__":
    print("--- Welcome to Monte Buster ---")

    # 1. Get User Pay Info
    user_pay_details = get_user_pay_info()

    # 2. Generate Pay Periods
    generated_pays = generate_pay_periods(user_pay_details)

    # 3. Load existing bills or get new ones
    bills_filename = "data/bills.json"
    user_bills = load_bills(bills_filename)
    if not user_bills:
        print("\nNo bills loaded. Let's add some new bills.")
        user_bills = get_user_bills()
        save_bills(user_bills, bills_filename)
    
    print(f"\nTotal Bills to manage: {len(user_bills)}")
    for bill in user_bills:
        print(f"  - Bill: {bill['name']}, Due: {bill['due_date']}, Amount: ${bill['amount']:.2f}, Category: {bill['category']}")

    # 4. Assign Bills to Paychecks
    final_pay_periods, unassigned_bills = assign_bills_to_paychecks(generated_pays, user_bills)

    # 5. Display Summary
    display_paycheck_summary(final_pay_periods, unassigned_bills)

    # --- Next steps would be to generate spreadsheet output ---
    # generate_spreadsheet_output(final_pay_periods)