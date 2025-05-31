# src/main.py
import datetime
import json
import csv # Add this import at the top of your file
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
#     'id': str,                  # Unique ID for each bill instance (e.g., 'Rent-2025-06')
#     'name': str,                # Name of the bill (e.g., 'Rent', 'Electricity')
#     'due_date': datetime.date,  # The date the bill is due (for this specific instance)
#     'amount': float,            # The amount of the bill
#     'category': str,            # Category (e.g., 'Housing', 'Utilities', 'Food')
#     'is_recurring': bool,       # True if this is a recurring bill
#     'recurrence_frequency': str or None, # 'monthly', 'bi-weekly', etc. (for the template bill)
#     'paid_by_paycheck_date': datetime.date or None # To link it back to the paycheck that covers it
# }

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

def add_bill():
    """
    Prompts the user for details of a single bill, including recurrence info.
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
        category = "Uncategorized"

    is_recurring = False
    recurrence_frequency = None

    while True:
        recurring_choice = input(f"Is {name} a recurring bill? (yes/no): ").lower().strip()
        if recurring_choice == "yes":
            is_recurring = True
            while True:
                freq = input("Enter recurrence frequency (monthly, bi-weekly): ").lower().strip()
                if freq in ["monthly", "bi-weekly"]: # We'll start with these two for now
                    recurrence_frequency = freq
                    break
                else:
                    print("Invalid frequency. Please enter 'monthly' or 'bi-weekly'.")
            break
        elif recurring_choice == "no":
            is_recurring = False
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    return {
        'id': f"{name}-{due_date.strftime('%Y%m%d')}", # Initial ID based on name and original due date
        'name': name,
        'due_date': due_date,
        'amount': amount,
        'category': category,
        'is_recurring': is_recurring,
        'recurrence_frequency': recurrence_frequency,
        'paid_by_paycheck_date': None
    }

def save_bills(bills, filename="data/bills.json"):
    """
    Saves a list of bill dictionaries to a JSON file.
    Converts datetime.date objects to strings for JSON serialization.
    """
    serializable_bills = []
    for bill in bills:
        temp_bill = bill.copy()
        if isinstance(temp_bill['due_date'], datetime.date):
            temp_bill['due_date'] = temp_bill['due_date'].strftime("%Y-%m-%d")
        # paid_by_paycheck_date might be None or a date object
        if temp_bill.get('paid_by_paycheck_date') and isinstance(temp_bill['paid_by_paycheck_date'], datetime.date):
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
        for bill_data in loaded_bills:
            # Convert date strings back to datetime.date objects
            if 'due_date' in bill_data and isinstance(bill_data['due_date'], str):
                bill_data['due_date'] = datetime.datetime.strptime(bill_data['due_date'], "%Y-%m-%d").date()
            if 'paid_by_paycheck_date' in bill_data and isinstance(bill_data['paid_by_paycheck_date'], str):
                bill_data['paid_by_paycheck_date'] = datetime.datetime.strptime(bill_data['paid_by_paycheck_date'], "%Y-%m-%d").date()
            elif 'paid_by_paycheck_date' in bill_data and bill_data['paid_by_paycheck_date'] == "null": # Handle case if json saves None as "null" string
                bill_data['paid_by_paycheck_date'] = None
            # Ensure new fields exist even if loading old data without them
            bill_data.setdefault('id', f"{bill_data['name']}-{bill_data['due_date'].strftime('%Y%m%d')}" if isinstance(bill_data['due_date'], datetime.date) else bill_data['name'])
            bill_data.setdefault('is_recurring', False)
            bill_data.setdefault('recurrence_frequency', None)

            bills.append(bill_data)
        print(f"Bills loaded from {filename}")
    except FileNotFoundError:
        print(f"No existing bill file found at {filename}. Starting with no bills.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}: {e}. Starting with no bills.")
    except Exception as e:
        print(f"An unexpected error occurred while loading bills: {e}. Starting with no bills.")
    return bills

# src/main.py (continued)

# ... (Your existing functions up to load_bills) ...

def generate_future_bill_instances(template_bills, end_date_horizon=datetime.date(2025, 12, 31)):
    """
    Generates all future instances of recurring bills until a specified end date.
    Returns a new list containing all one-time bills and generated recurring bill instances.
    """
    all_bill_instances = []
    
    for bill in template_bills:
        if not bill['is_recurring']:
            # Add one-time bills directly
            all_bill_instances.append(bill)
            continue # Move to the next bill

        # Handle recurring bills
        current_due_date = bill['due_date']
        
        # Determine the start point for generating instances
        # We need to consider bills that are due today or in the future
        # or recurring bills that might have had their first instance due slightly before today
        # but the *next* instance is still relevant.
        # For simplicity, let's generate from the *initial* due date onward if it's within the horizon,
        # otherwise from the next relevant due date.
        
        # If the first instance is already past, skip it for future generation,
        # but ensure the initial bill (from template_bills) is not duplicated if it was recent/future.
        
        # Ensure we don't add the template bill itself if it's past and not the first instance for this run
        # The key here is to generate *new* instances for future payments.
        
        # If the template bill's due_date is in the past,
        # we need to find the *first upcoming* due date for its recurrence.
        if current_due_date < datetime.date.today():
            if bill['recurrence_frequency'] == 'monthly':
                # Advance month by month until it's today or in the future
                while current_due_date < datetime.date.today():
                    # Handle end-of-month dates for monthly recurrence
                    # E.g., if due on Jan 31, next is Feb 28/29, then Mar 31
                    try:
                        current_due_date = current_due_date.replace(month=current_due_date.month + 1)
                    except ValueError: # Handle month overflow (Dec -> Jan)
                        current_due_date = current_due_date.replace(year=current_due_date.year + 1, month=1)
            elif bill['recurrence_frequency'] == 'bi-weekly':
                # Advance two weeks at a time until it's today or in the future
                while current_due_date < datetime.date.today():
                    current_due_date += datetime.timedelta(days=14)


        # Now, generate instances from the current_due_date onwards
        while current_due_date <= end_date_horizon:
            # Create a new bill instance (copy the original, but update date and ID)
            new_bill_instance = bill.copy()
            new_bill_instance['due_date'] = current_due_date
            # Create a unique ID for each instance (e.g., Rent-2025-06-01)
            new_bill_instance['id'] = f"{bill['name']}-{current_due_date.strftime('%Y%m%d')}"
            new_bill_instance['paid_by_paycheck_date'] = None # Reset for new instance

            all_bill_instances.append(new_bill_instance)

            # Move to the next due date based on frequency
            if bill['recurrence_frequency'] == 'monthly':
                # Handle end-of-month dates (e.g., Jan 31 -> Feb 28 -> Mar 31)
                try:
                    current_due_date = current_due_date.replace(month=current_due_date.month + 1)
                except ValueError: # Month overflow (Dec -> Jan)
                    current_due_date = current_due_date.replace(year=current_due_date.year + 1, month=1)
            elif bill['recurrence_frequency'] == 'bi-weekly':
                current_due_date += datetime.timedelta(days=14)
            # Add other frequencies here if needed (e.g., 'weekly', 'quarterly')

    # Sort all instances by due date
    all_bill_instances.sort(key=lambda b: b['due_date'])
    return all_bill_instances

def assign_bills_to_paychecks(pay_periods, bills):
    """
    Assigns bills to the earliest possible paycheck based on their due date,
    considering a grace period for bills due shortly after a paycheck.
    Prioritizes earlier due dates.
    """
    # Bills are already sorted by due date from generate_future_bill_instances

    # Make a copy of pay_periods to work with, as we'll modify remaining_balance
    # and assigned_bills for each period
    assigned_pay_periods = [p.copy() for p in pay_periods]
    for pp in assigned_pay_periods:
        pp['assigned_bills'] = [] # Ensure this is a new empty list for each copy
        pp['remaining_balance'] = pp['net_pay'] # Reset for fresh assignment

    unassigned_bills = []

    # Define a window for assigning bills
    # A bill due within GRACE_DAYS_AFTER_PAYCHECK days *after* a paycheck date
    # can be covered by that preceding paycheck.
    # This addresses bills due early next month (e.g., 1st) being paid by a
    # paycheck at the end of the current month.
    GRACE_DAYS_AFTER_PAYCHECK = 5 # Example: A bill due up to 7 days after a paycheck can be covered by it

    for bill in bills:
        assigned = False
        for pay_period in assigned_pay_periods:
            # Condition 1: Paycheck is on or after the bill's due date (standard assignment)
            condition1 = (pay_period['pay_date'] >= bill['due_date'])

            # Condition 2: Paycheck is *before* the bill's due date, BUT
            # the bill's due date falls within a "grace period" (e.g., 7 days)
            # *after* this paycheck's date.
            # This is crucial for bills like Rent (due 1st) paid by end-of-month paycheck.
            condition2 = (pay_period['pay_date'] < bill['due_date'] and
                          bill['due_date'] <= (pay_period['pay_date'] + datetime.timedelta(days=GRACE_DAYS_AFTER_PAYCHECK)))

            # Check if bill can be assigned to this pay period based on date window and sufficient funds
            if (condition1 or condition2) and \
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

def generate_spreadsheet_output(pay_periods, base_filename="data/financial_plan.csv"):
    """
    Generates a chronological CSV file containing all financial transactions
    (paychecks and assigned bills) with a running balance.
    Attempts to save to base_filename. If permission denied, saves to a timestamped file.
    """
    fieldnames = ['Date', 'Type', 'Description', 'Amount', 'Balance_Impact', 'Running_Balance_After_Transaction']

    all_transactions = []
    
    # 1. Collect all transactions into a single list
    for pp in pay_periods:
        # Add the paycheck transaction
        all_transactions.append({
            'Date': pp['pay_date'], # Use datetime.date object for sorting
            'Type': 'Paycheck',
            'Description': 'Net Pay Received',
            'Amount': pp['net_pay'],
            'Balance_Impact': f"+{pp['net_pay']:.2f}"
        })

        # Add each assigned bill as a separate transaction
        for bill in pp['assigned_bills']:
            all_transactions.append({
                'Date': bill['due_date'], # Use bill's due date for its transaction entry
                'Type': 'Bill Payment',
                'Description': bill['name'],
                'Amount': -bill['amount'], # Negative for expense
                'Balance_Impact': f"-{bill['amount']:.2f}"
            })

    # 2. Sort all transactions chronologically by their date
    all_transactions.sort(key=lambda x: x['Date'])

    # --- Now, write the sorted transactions to CSV with a running balance ---

    # Helper function to write to CSV, handles the actual file writing logic
    def write_to_csv(output_filename):
        with open(output_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            global_running_balance = 0.0 # Initialize a true running balance across all transactions

            for transaction in all_transactions:
                global_running_balance += transaction['Amount'] # Update running balance
                
                writer.writerow({
                    'Date': transaction['Date'].strftime('%Y-%m-%d'), # Format date for CSV
                    'Type': transaction['Type'],
                    'Description': transaction['Description'],
                    'Amount': transaction['Amount'],
                    'Balance_Impact': transaction['Balance_Impact'],
                    'Running_Balance_After_Transaction': f"{global_running_balance:.2f}"
                })
        print(f"Financial plan exported to {output_filename}")

    # --- Attempt to write to the base filename, with fallback for permission errors ---
    try:
        write_to_csv(base_filename)
    except IOError as e:
        if "Permission denied" in str(e):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dir_name = os.path.dirname(base_filename)
            file_name_without_ext = os.path.splitext(os.path.basename(base_filename))[0]
            ext = os.path.splitext(os.path.basename(base_filename))[1]

            timestamped_filename = os.path.join(dir_name, f"{file_name_without_ext}_{timestamp}{ext}")

            print(f"Permission denied for {base_filename}. Attempting to save to {timestamped_filename}...")
            try:
                write_to_csv(timestamped_filename)
            except IOError as e_fallback:
                print(f"Still unable to export financial plan (even with timestamp) due to: {e_fallback}")
            except Exception as e_gen:
                print(f"An unexpected error occurred during timestamped export: {e_gen}")
        else:
            print(f"Error exporting financial plan to {base_filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during export: {e}")

if __name__ == "__main__":
    print("--- Welcome to Monte Buster ---")

    # 1. Get User Pay Info
    user_pay_details = get_user_pay_info()

    # 2. Generate Pay Periods
    generated_pays = generate_pay_periods(user_pay_details)

    # 3. Load existing bills first
    bills_filename = "data/bills.json"
    template_bills = load_bills(bills_filename) # Always attempt to load existing bills

    # 4. Give the option to add more bills (or new ones if none were loaded)
    print(f"\nCurrently managing {len(template_bills)} template bills.")
    
    # Use a loop to allow adding multiple new bills in one session if desired
    while True:
        add_more_choice = input("Do you want to add NEW bills or modify existing ones? (yes/no): ").lower().strip()
        if add_more_choice == "yes":
            # If the user wants to add, call get_user_bills which loops until they say 'no'
            newly_added_bills = get_user_bills()
            template_bills.extend(newly_added_bills) # Add the new bills to the existing list
            save_bills(template_bills, bills_filename) # Save the updated list immediately
            print("\nBills list updated and saved.")
            # After adding, give them the option to add even more, or proceed
            continue # Loop back to ask if they want to add more
        elif add_more_choice == "no":
            break # Exit the loop if they don't want to add more
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")


    print(f"\nFinal list of {len(template_bills)} template bills:")
    for bill in template_bills:
        print(f"  - Bill: {bill['name']}, Due: {bill['due_date']}, Amount: ${bill['amount']:.2f}, Recurring: {bill['is_recurring']}")

    # 5. Generate all future bill instances (for recurring bills)
    all_bill_instances = generate_future_bill_instances(template_bills)
    print(f"\nGenerated {len(all_bill_instances)} total bill instances for planning until end of 2025.")

    # 6. Assign Bills to Paychecks
    final_pay_periods, unassigned_bills = assign_bills_to_paychecks(generated_pays, all_bill_instances)

    # 7. Display Summary (to console)
    display_paycheck_summary(final_pay_periods, unassigned_bills)

    # 8. Generate Spreadsheet Output (this will always overwrite for a fresh plan)
    generate_spreadsheet_output(final_pay_periods, "data/financial_plan.csv")