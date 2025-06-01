import datetime
from datetime import datetime, date, timedelta
import uuid
import re
import os
import json
import pandas as pd # For spreadsheet generation

# --- Helper Functions ---

def get_user_input(prompt):
    """
    Standardizes getting string input from the user.
    """
    return input(prompt)

def get_user_date_input(prompt):
    """
    Helper function to get valid date input from user, loops until valid.
    """
    while True:
        date_str = input(prompt).strip()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use ISO-MM-DD.")

def get_user_float_input(prompt, allow_negative=False):
    """
    Helper function to get valid float input from user, loops until valid.
    """
    while True:
        value_str = input(prompt).strip().replace('$', '')
        try:
            value = float(value_str)
            if not allow_negative and value < 0:
                print("Value cannot be negative. Please enter a positive numerical value.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a numerical value.")

def get_user_int_input(prompt, min_val=None, max_val=None):
    """
    Helper function to get valid integer input from user, loops until valid.
    """
    while True:
        value_str = input(prompt).strip()
        try:
            value = int(value_str)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
            elif max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


def load_bills(file_path='data/bills.json'):
    """
    Loads bill templates from a JSON file.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        bills_data = json.load(f)
    
    # Convert date strings back to datetime.date objects and ensure floats
    for bill in bills_data:
        if 'due_date' in bill and isinstance(bill['due_date'], str):
            bill['due_date'] = datetime.strptime(bill['due_date'], "%Y-%m-%d").date()
        
        # Ensure all numeric fields are floats upon loading and handle potential None values
        for key in ['amount', 'initial_balance', 'minimum_payment', 'interest_rate', 'credit_limit', 'monthly_fee', 'annual_fee']:
            if key in bill and bill[key] is not None:
                try:
                    bill[key] = float(bill[key])
                except ValueError:
                    print(f"Warning: Could not convert {bill[key]} for {key} in bill {bill.get('name', 'Unknown')}. Setting to 0.0")
                    bill[key] = 0.0 # Default to 0.0 if conversion fails
        if 'annual_fee_month' in bill and bill['annual_fee_month'] is not None:
            try:
                bill['annual_fee_month'] = int(bill['annual_fee_month'])
            except ValueError:
                print(f"Warning: Could not convert {bill['annual_fee_month']} for annual_fee_month in bill {bill.get('name', 'Unknown')}. Setting to None")
                bill['annual_fee_month'] = None # Default to None if conversion fails


    return bills_data

def save_bills(bills, file_path='data/bills.json'):
    """
    Saves bill templates to a JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert datetime.date objects to string for JSON serialization
    bills_to_save = []
    for bill in bills:
        bill_copy = bill.copy()
        if 'due_date' in bill_copy and isinstance(bill_copy['due_date'], date):
            bill_copy['due_date'] = bill_copy['due_date'].strftime("%Y-%m-%d")
        bills_to_save.append(bill_copy)

    with open(file_path, 'w') as f:
        json.dump(bills_to_save, f, indent=4)

# --- Main Functions ---

def add_bill():
    """
    Prompts the user to add a new bill (template).
    """
    bill = {}

    bill['id'] = str(uuid.uuid4()) # Generate a unique ID for the template bill

    bill['name'] = get_user_input("Enter bill name (e.g., Rent, Phone, Credit Card): ").strip()

    # Determine if it's a debt account based on keywords or user input
    debt_keywords = ["credit card", "loan", "debt", "mortgage", "car loan", "student loan"]
    
    is_debt_default = "no"
    if any(keyword in bill['name'].lower() for keyword in debt_keywords):
        is_debt_default = "yes"

    while True:
        is_debt_choice = input(f"Is '{bill['name']}' a debt account (e.g., credit card, loan)? ({is_debt_default}/no): ").lower().strip()
        if is_debt_choice == "yes" or (is_debt_choice == "" and is_debt_default == "yes"):
            bill['is_debt'] = True
            
            # --- Debt-specific fields ---
            bill['initial_balance'] = get_user_float_input(f"Enter initial balance for {bill['name']}: $")
            bill['minimum_payment'] = get_user_float_input(f"Enter minimum payment for {bill['name']}: $")
            bill['interest_rate'] = get_user_float_input(f"Enter annual interest rate for {bill['name']} (e.g., 0.18 for 18%): ", allow_negative=False)
            bill['credit_limit'] = get_user_float_input(f"Enter credit limit for {bill['name']} (e.g., 2000.00, or 0 if not applicable): $")
            bill['monthly_fee'] = get_user_float_input(f"Enter monthly fee for {bill['name']} (e.g., 10.00, enter 0 if none): $")
            bill['annual_fee'] = get_user_float_input(f"Enter annual fee for {bill['name']} (e.g., 99.00, enter 0 if none): $")
            
            # If there's an annual fee, ask for the month it's charged
            if bill['annual_fee'] > 0:
                bill['annual_fee_month'] = get_user_int_input(f"Enter the month (1-12) when the annual fee is charged for {bill['name']}: ", 1, 12)
            else:
                bill['annual_fee_month'] = None # No annual fee, so no annual fee month

            break # Exit the is_debt_choice loop
        
        elif is_debt_choice == "no" or (is_debt_choice == "" and is_debt_default == "no"):
            bill['is_debt'] = False
            # Set debt-specific fields to None if not a debt
            bill['initial_balance'] = None
            bill['current_balance'] = None 
            bill['minimum_payment'] = None
            bill['interest_rate'] = None
            bill['credit_limit'] = None
            bill['monthly_fee'] = None
            bill['annual_fee'] = None
            bill['annual_fee_month'] = None
            break # Exit the is_debt_choice loop
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
            
    # --- General Bill Fields (applicable to all bills) ---
    bill['due_date'] = get_user_date_input("Enter bill due date (YYYY-MM-DD) for initial setup: ")

    bill['amount'] = get_user_float_input(f"Enter default amount for {bill['name']} (for non-debt bills, this is the bill amount; for debts, this is typically your planned payment): $")
    
    while True:
        is_recurring_str = input(f"Is {bill['name']} a recurring bill? (yes/no): ").lower().strip()
        if is_recurring_str == 'yes':
            bill['is_recurring'] = True
            bill['recurrence_frequency'] = get_user_input("Enter recurrence frequency (e.g., monthly, bi-weekly, annually): ").strip().lower()
            break
        elif is_recurring_str == 'no':
            bill['is_recurring'] = False
            bill['recurrence_frequency'] = None
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    bill['category'] = get_user_input(f"Enter category for {bill['name']} (e.g., Housing, Utilities, Transportation, Debt, Subscription): ").strip()
    
    # Initialize these for new bills
    bill['paid_by_paycheck_date'] = None # This will be filled later by assignment logic

    return bill

def view_bills(bills):
    """
    Displays all loaded bill templates in a formatted list.
    """
    if not bills:
        print("\nNo bills currently loaded. Please add some bills first.")
        return False # Indicate no bills to view

    print("\n--- Current Bill Templates ---")
    for i, bill in enumerate(bills):
        print(f"{i + 1}. Name: {bill['name']}")
        print(f"   Due Date: {bill['due_date'].strftime('%Y-%m-%d')}")
        print(f"   Amount: ${bill['amount']:.2f}")
        print(f"   Recurring: {'Yes' if bill['is_recurring'] else 'No'}")
        if bill['is_recurring']:
            print(f"   Frequency: {bill['recurrence_frequency']}")
        print(f"   Category: {bill['category']}")
        if bill.get('is_debt', False):
            print(f"   -- Debt Details --")
            print(f"   Initial Balance: ${bill['initial_balance']:.2f}")
            print(f"   Min Payment: ${bill['minimum_payment']:.2f}")
            print(f"   Interest Rate: {bill['interest_rate'] * 100:.2f}% (Annual)")
            print(f"   Credit Limit: ${bill['credit_limit']:.2f}")
            if bill.get('monthly_fee', 0.0) > 0:
                print(f"   Monthly Fee: ${bill['monthly_fee']:.2f}")
            if bill.get('annual_fee', 0.0) > 0:
                print(f"   Annual Fee: ${bill['annual_fee']:.2f} (Month: {bill['annual_fee_month']})")
        print("-" * 20)
    return True # Indicate bills were displayed

def edit_bill(bills):
    """
    Allows the user to select and edit an existing bill template.
    """
    if not view_bills(bills):
        return # No bills to edit

    while True:
        try:
            bill_index_str = get_user_input("Enter the number of the bill to edit (or 0 to cancel): ").strip()
            bill_index = int(bill_index_str) - 1

            if bill_index == -1: # User entered 0 to cancel
                print("Bill editing cancelled.")
                return

            if 0 <= bill_index < len(bills):
                selected_bill = bills[bill_index]
                print(f"\n--- Editing Bill: {selected_bill['name']} ---")
                
                # Display editable fields
                print("Select field to edit:")
                print("1. Name")
                print("2. Due Date (YYYY-MM-DD)")
                print("3. Amount")
                print("4. Recurring (yes/no)")
                if selected_bill['is_recurring']:
                    print("5. Recurrence Frequency")
                print("6. Category")
                if selected_bill.get('is_debt', False):
                    print("7. Initial Balance")
                    print("8. Minimum Payment")
                    print("9. Interest Rate")
                    print("10. Credit Limit")
                    print("11. Monthly Fee")
                    print("12. Annual Fee")
                    if selected_bill.get('annual_fee', 0.0) > 0:
                        print("13. Annual Fee Month")
                print("0. Done editing this bill")

                while True:
                    field_choice = get_user_input("Enter field number to edit: ").strip()

                    if field_choice == '0':
                        print(f"Finished editing '{selected_bill['name']}'.")
                        save_bills(bills) # Save after each bill is done editing
                        return # Exit editing for this bill

                    if field_choice == '1':
                        selected_bill['name'] = get_user_input(f"Enter new name for {selected_bill['name']}: ").strip()
                    elif field_choice == '2':
                        selected_bill['due_date'] = get_user_date_input(f"Enter new due date for {selected_bill['name']} (YYYY-MM-DD): ")
                    elif field_choice == '3':
                        selected_bill['amount'] = get_user_float_input(f"Enter new amount for {selected_bill['name']}: $")
                    elif field_choice == '4':
                        while True:
                            is_recurring_str = input(f"Is {selected_bill['name']} a recurring bill? (yes/no): ").lower().strip()
                            if is_recurring_str == 'yes':
                                selected_bill['is_recurring'] = True
                                selected_bill['recurrence_frequency'] = get_user_input("Enter new recurrence frequency (e.g., monthly, bi-weekly, annually): ").strip().lower()
                                break
                            elif is_recurring_str == 'no':
                                selected_bill['is_recurring'] = False
                                selected_bill['recurrence_frequency'] = None
                                break
                            else:
                                print("Invalid choice. Please enter 'yes' or 'no'.")
                    elif field_choice == '5' and selected_bill['is_recurring']:
                        selected_bill['recurrence_frequency'] = get_user_input("Enter new recurrence frequency (e.g., monthly, bi-weekly, annually): ").strip().lower()
                    elif field_choice == '6':
                        selected_bill['category'] = get_user_input(f"Enter new category for {selected_bill['name']}: ").strip()
                    elif selected_bill.get('is_debt', False) and field_choice == '7':
                        selected_bill['initial_balance'] = get_user_float_input(f"Enter new initial balance for {selected_bill['name']}: $")
                    elif selected_bill.get('is_debt', False) and field_choice == '8':
                        selected_bill['minimum_payment'] = get_user_float_input(f"Enter new minimum payment for {selected_bill['name']}: $")
                    elif selected_bill.get('is_debt', False) and field_choice == '9':
                        selected_bill['interest_rate'] = get_user_float_input(f"Enter new annual interest rate for {selected_bill['name']} (e.g., 0.18 for 18%): ", allow_negative=False)
                    elif selected_bill.get('is_debt', False) and field_choice == '10':
                        selected_bill['credit_limit'] = get_user_float_input(f"Enter new credit limit for {selected_bill['name']}: $")
                    elif selected_bill.get('is_debt', False) and field_choice == '11':
                        selected_bill['monthly_fee'] = get_user_float_input(f"Enter new monthly fee for {selected_bill['name']} (enter 0 if none): $")
                    elif selected_bill.get('is_debt', False) and field_choice == '12':
                        selected_bill['annual_fee'] = get_user_float_input(f"Enter new annual fee for {selected_bill['name']} (enter 0 if none): $")
                        if selected_bill['annual_fee'] > 0:
                            selected_bill['annual_fee_month'] = get_user_int_input(f"Enter the month (1-12) when the annual fee is charged for {selected_bill['name']}: ", 1, 12)
                        else:
                            selected_bill['annual_fee_month'] = None
                    elif selected_bill.get('is_debt', False) and selected_bill.get('annual_fee', 0.0) > 0 and field_choice == '13':
                        selected_bill['annual_fee_month'] = get_user_int_input(f"Enter the month (1-12) when the annual fee is charged for {selected_bill['name']}: ", 1, 12)
                    else:
                        print("Invalid field number or field not applicable to this bill type. Please try again.")
                    
                    # This line attempts to get a key by index, which is not reliable for dictionaries.
                    # It's better to just confirm the update generally.
                    # print(f"'{selected_bill['name']}' updated. Current value: {selected_bill.get(list(selected_bill.keys())[int(field_choice)-1], 'N/A')}") # Basic confirmation
                    print(f"'{selected_bill['name']}' updated.") # Simpler confirmation
                    view_bills([selected_bill]) # Show updated bill
            else:
                print("Invalid bill number. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except IndexError:
            print("Invalid bill number. Please enter a number from the list.")

def generate_bill_instances(bill_templates, start_date, end_date):
    """
    Generates instances of recurring bills based on templates within a date range.
    """
    bill_instances = []
    
    # Convert start_date and end_date to date objects if they are strings (shouldn't happen with get_user_date_input)
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    for template in bill_templates:
        # Debts are not "generated instances" in the same way; their payments are part of the simulation
        # However, if a 'debt payment' is entered as a recurring bill (e.g. 'Credit Card Payment'), it will be processed here
        # For simplicity, we assume 'amount' for debt templates is the intended payment, and it will be assigned.
        # The debt simulation itself uses minimum_payment if no assigned payment is found for a month.

        if template['is_recurring']:
            current_due_date = template['due_date']
            
            # Adjust current_due_date to be within or past start_date if it's an old template
            # Ensure we don't start generating instances from before our planning period
            while current_due_date < start_date:
                if template['recurrence_frequency'] == 'monthly':
                    if current_due_date.month == 12:
                        current_due_date = current_due_date.replace(year=current_due_date.year + 1, month=1)
                    else:
                        current_due_date = current_due_date.replace(month=current_due_date.month + 1)
                elif template['recurrence_frequency'] == 'bi-weekly':
                    current_due_date += timedelta(weeks=2)
                elif template['recurrence_frequency'] == 'annually':
                    current_due_date = current_due_date.replace(year=current_due_date.year + 1)
                else:
                    break # Break if frequency is unknown, avoid infinite loop for bad data

            # Now, iterate from the adjusted current_due_date
            while current_due_date <= end_date:
                instance = template.copy()
                instance['id'] = str(uuid.uuid4()) # Unique ID for each instance
                instance['due_date'] = current_due_date
                instance['paid_by_paycheck_date'] = None # Reset for each instance
                bill_instances.append(instance)

                # Move to the next due date based on frequency
                if template['recurrence_frequency'] == 'monthly':
                    if current_due_date.month == 12:
                        current_due_date = current_due_date.replace(year=current_due_date.year + 1, month=1)
                    else:
                        current_due_date = current_due_date.replace(month=current_due_date.month + 1)
                elif template['recurrence_frequency'] == 'bi-weekly':
                    current_due_date += timedelta(weeks=2)
                elif template['recurrence_frequency'] == 'annually':
                    current_due_date = current_due_date.replace(year=current_due_date.year + 1)
                else:
                    print(f"Warning: Unknown recurrence frequency for {template['name']}: {template['recurrence_frequency']}")
                    break # Stop generating instances for this bill if frequency is unknown
        else:
            # For non-recurring bills, just add the single instance if within range
            if start_date <= template['due_date'] <= end_date:
                instance = template.copy()
                instance['id'] = str(uuid.uuid4()) # Unique ID for each instance
                instance['paid_by_paycheck_date'] = None
                bill_instances.append(instance)
    
    # Sort bill instances by due date
    bill_instances.sort(key=lambda x: x['due_date'])
    
    return bill_instances

def assign_bills_to_paychecks(bill_instances, num_paychecks, net_pay, start_date):
    """
    Assigns bills to paychecks over a specified period.
    Assumes bi-weekly paychecks starting from start_date.
    """
    paychecks = []
    current_pay_date = start_date

    # Determine planning end date based on paychecks
    # Assuming start_date is the date of the first paycheck.
    # The simulation period should cover all bills until the last paycheck.
    end_planning_date = start_date + timedelta(weeks=2 * (num_paychecks - 1)) # Date of the last paycheck
    
    # Filter out bill instances that are outside the full planning period
    # This ensures only relevant bills are considered, even if due dates extend slightly past a paycheck
    filtered_bill_instances = [
        bill for bill in bill_instances 
        if bill['due_date'] <= end_planning_date + timedelta(days=31) # Allow bills due a month after last paycheck
    ]
    # Sort by due date
    filtered_bill_instances.sort(key=lambda x: x['due_date'])

    # Track unassigned bills that carry over
    unassigned_carry_over_bills = []

    for i in range(num_paychecks):
        paycheck_info = {
            'pay_date': current_pay_date,
            'net_pay': net_pay,
            'initial_balance_for_period': net_pay,
            'assigned_bills': [],
            'remaining_balance': net_pay
        }
        
        # Add any carried-over unassigned bills to the current paycheck's consideration
        # Process carry-over bills first
        for bill in unassigned_carry_over_bills[:]: # Iterate over copy
            if paycheck_info['remaining_balance'] >= bill['amount']:
                paycheck_info['assigned_bills'].append(bill)
                paycheck_info['remaining_balance'] -= bill['amount']
                bill['paid_by_paycheck_date'] = current_pay_date # Mark as paid
                unassigned_carry_over_bills.remove(bill) # Remove from carry-over list
            # Else, it remains in unassigned_carry_over_bills for the next paycheck
        
        # Identify bills due before the *next* paycheck (or end of planning if last paycheck)
        next_pay_date = current_pay_date + timedelta(weeks=2)
        
        # Bills due between previous paycheck + 1 day and next paycheck due date
        bills_due_this_period = []
        for bill in filtered_bill_instances:
            # If bill is not already paid/assigned AND its due date is relevant for this paycheck window
            if bill.get('paid_by_paycheck_date') is None and bill['due_date'] <= next_pay_date:
                bills_due_this_period.append(bill)
        
        # Sort new bills for this period by due date, then by amount (largest first)
        bills_due_this_period.sort(key=lambda x: (x['due_date'], -x['amount']))

        # Assign new bills due this period
        for bill in bills_due_this_period:
            if bill.get('paid_by_paycheck_date') is None: # Only assign if not already assigned (prevents double assignment if it was a carry-over)
                if paycheck_info['remaining_balance'] >= bill['amount']:
                    paycheck_info['assigned_bills'].append(bill)
                    paycheck_info['remaining_balance'] -= bill['amount']
                    bill['paid_by_paycheck_date'] = current_pay_date # Mark as paid
                else:
                    unassigned_carry_over_bills.append(bill) # Carry over if insufficient funds

        paychecks.append(paycheck_info)
        current_pay_date += timedelta(weeks=2)

    return paychecks

def display_paycheck_summary(final_pay_periods):
    """
    Displays a summary of assigned bills per paycheck.
    """
    print("\n" + "="*50)
    print(" " * 10 + "MONTE BUSTER: FINANCIAL OVERVIEW")
    print("="*50 + "\n")

    total_bills_generated = sum(len(pp['assigned_bills']) for pp in final_pay_periods)
    print(f"Total paychecks planned: {len(final_pay_periods)}")
    print(f"Generated {total_bills_generated} total bill instances for planning until {final_pay_periods[-1]['pay_date'].strftime('%Y-%m-%d') if final_pay_periods else 'N/A'}.\n")


    for pp in final_pay_periods:
        print(f"--- Paycheck Date: {pp['pay_date'].strftime('%Y-%m-%d')} ---")
        print(f"  Net Pay: ${pp['net_pay']:.2f}")
        print(f"  Initial Balance for Period: ${pp['initial_balance_for_period']:.2f}")
        print("  Assigned Bills:")
        if not pp['assigned_bills']:
            print("    None")
        for bill in pp['assigned_bills']:
            print(f"    - {bill['name']:<20} (Due: {bill['due_date'].strftime('%m-%d')}) - ${bill['amount']:.2f}")
        print(f"  **Remaining Balance: ${pp['remaining_balance']:.2f}**")
        print("-" * 30 + "\n")

def simulate_debt_progress(template_bills, final_pay_periods):
    """
    Simulates the progress of debt payments and interest accrual over time.
    Tracks balance reduction for each debt account.
    
    Args:
        template_bills (list): Original list of template bills, including debt details.
        final_pay_periods (list): List of pay periods with assigned bills.

    Returns:
        dict: A dictionary where keys are debt names and values are lists of
              monthly snapshots of debt balance, interest paid, etc.
    """
    
    # Initialize live debt accounts from templates
    live_debt_accounts = {}
    for bill_template in template_bills:
        if bill_template.get('is_debt', False) and bill_template.get('initial_balance') is not None and bill_template['initial_balance'] > 0:
            debt_name = bill_template['name']
            live_debt_accounts[debt_name] = {
                'name': debt_name,
                'current_balance': float(bill_template['initial_balance']), 
                'minimum_payment': float(bill_template['minimum_payment']),
                'interest_rate': float(bill_template['interest_rate']), # Annual rate (e.g., 0.24)
                'credit_limit': float(bill_template['credit_limit']),
                'monthly_fee': float(bill_template.get('monthly_fee', 0.0)),
                'annual_fee': float(bill_template.get('annual_fee', 0.0)),
                'annual_fee_month': bill_template.get('annual_fee_month'),
                'history': [] # To store monthly snapshots of balance, interest, etc.
            }
    
    if not live_debt_accounts:
        print("\nNo active debt accounts with a balance to simulate.")
        return {}

    print("\n--- Simulating Debt Progress ---")

    # Group payments by debt and by month for easier processing
    # Key: (year, month), Value: { debt_name: total_paid_this_month }
    payments_by_month_and_debt = {} 
    
    # Determine the earliest and latest payment month based on assigned bills
    # If no payments, use today's month as min and 6 months from now as max
    min_year, min_month = date.today().year, date.today().month
    max_year, max_month = (date.today() + timedelta(days=180)).year, (date.today() + timedelta(days=180)).month


    if final_pay_periods:
        first_pay_date = final_pay_periods[0]['pay_date']
        last_pay_date = final_pay_periods[-1]['pay_date']
        
        min_year, min_month = first_pay_date.year, first_pay_date.month
        max_year, max_month = last_pay_date.year, last_pay_date.month

        for pp in final_pay_periods:
            pay_date = pp['pay_date']
            payment_month_key = (pay_date.year, pay_date.month)
            
            for assigned_bill in pp['assigned_bills']:
                if assigned_bill.get('is_debt', False) and assigned_bill['name'] in live_debt_accounts:
                    debt_name = assigned_bill['name']
                    
                    payments_by_month_and_debt.setdefault(payment_month_key, {}).setdefault(debt_name, 0.0)
                    payments_by_month_and_debt[payment_month_key][debt_name] += assigned_bill['amount']
    
    
    # Set the simulation start date (beginning of the month of the first payment or today)
    start_sim_date = date(min_year, min_month, 1)
    if start_sim_date < date.today().replace(day=1):
        start_sim_date = date.today().replace(day=1)

    # Set the simulation end date (end of the month of the last payment, or later to see payoff)
    end_sim_date_raw = date(max_year, max_month, 1)
    if end_sim_date_raw.month == 12:
        end_sim_date = end_sim_date_raw.replace(year=end_sim_date_raw.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_sim_date = end_sim_date_raw.replace(month=end_sim_date_raw.month + 1, day=1) - timedelta(days=1)
    
    # Extend simulation for a few more months just in case debts take longer to pay off
    end_sim_date += timedelta(days=365) # Extend by another year for simulation

    current_sim_date = start_sim_date

    # Iterate month by month strictly until the determined end date
    simulation_months_counter = 0
    while current_sim_date <= end_sim_date and simulation_months_counter < 120: # Cap at 10 years to prevent infinite loops
        year = current_sim_date.year
        month = current_sim_date.month

        print(f"\n--- Month: {year}-{month:02d} ---")
        
        # Check if all debts are paid off at the beginning of the month
        all_debts_paid_this_month = True
        for debt_name, debt_data in live_debt_accounts.items():
            if debt_data['current_balance'] > 0:
                all_debts_paid_this_month = False
                break
        if all_debts_paid_this_month:
            print("All active debts paid off!")
            break


        for debt_name, debt_data in live_debt_accounts.items():
            current_balance = debt_data['current_balance']
            
            if current_balance <= 0:
                if not debt_data['history'] or debt_data['history'][-1]['date'].month != current_sim_date.month or debt_data['history'][-1]['date'].year != current_sim_date.year:
                    debt_data['history'].append({
                        'date': current_sim_date,
                        'balance_start_of_month': 0.0,
                        'total_fees_charged': 0.0, 
                        'payments_made': 0.0,
                        'interest_accrued': 0.0,
                        'principal_paid': 0.0,
                        'balance_end_of_month': 0.0
                    })
                # Only print "Paid off!" once per debt
                if not debt_data['history'] or debt_data['history'][-1]['balance_end_of_month'] > 0:
                    print(f"  - {debt_name}: Paid off! (Balance: $0.00)")
                continue

            # --- APPLY MONTHLY AND ANNUAL FEES ---
            total_fees_this_month = 0.0
            
            # Apply monthly fee
            monthly_fee = debt_data.get('monthly_fee', 0.0)
            if monthly_fee > 0:
                total_fees_this_month += monthly_fee
                # current_balance += monthly_fee # Apply after interest calc, or account for interest on fee if immediate
                # print(f"  - {debt_name}: Monthly Fee of ${monthly_fee:.2f} charged.") # Removed for cleaner output
            
            # Apply annual fee if applicable for this month
            annual_fee = debt_data.get('annual_fee', 0.0)
            annual_fee_month = debt_data.get('annual_fee_month')
            if annual_fee > 0 and annual_fee_month == month:
                total_fees_this_month += annual_fee
                # current_balance += annual_fee # Apply after interest calc, or account for interest on fee if immediate
                # print(f"  - {debt_name}: Annual Fee of ${annual_fee:.2f} charged.") # Removed for cleaner output
            # --- END FEE LOGIC ---

            annual_interest_rate = debt_data['interest_rate']
            monthly_interest_rate = annual_interest_rate / 12.0

            # Interest is typically calculated on the balance *before* the current month's payment.
            # Fees can also accrue interest if added before interest calculation.
            interest_accrued_this_month = current_balance * monthly_interest_rate
            current_balance_after_interest_and_fees = current_balance + interest_accrued_this_month + total_fees_this_month
            
            payments_this_month = payments_by_month_and_debt.get((year, month), {}).get(debt_name, 0.0)
            
            new_balance = current_balance_after_interest_and_fees - payments_this_month
            
            if new_balance < 0:
                new_balance = 0.0
            
            # Calculate principal paid: total payments minus interest and fees for this month
            principal_paid_this_month = payments_this_month - (interest_accrued_this_month + total_fees_this_month)
            if principal_paid_this_month < 0:
                principal_paid_this_month = 0.0 
            
            debt_data['current_balance'] = new_balance

            # Record snapshot
            debt_data['history'].append({
                'date': current_sim_date,
                'balance_start_of_month': round(current_balance, 2), # Balance before any actions this month
                'total_fees_charged': round(total_fees_this_month, 2), 
                'payments_made': round(payments_this_month, 2),
                'interest_accrued': round(interest_accrued_this_month, 2),
                'principal_paid': round(principal_paid_this_month, 2),
                'balance_end_of_month': round(new_balance, 2)
            })

            fee_print_str = ""
            if total_fees_this_month > 0:
                fee_print_str = f" (+Fees: ${total_fees_this_month:.2f})"

            print(f"  - {debt_name}: Beg Bal: ${current_balance:.2f}{fee_print_str}"
                  f", Interest: ${interest_accrued_this_month:.2f}, Paid: ${payments_this_month:.2f}, End Bal: ${new_balance:.2f}")
            
        # Move to the next month
        simulation_months_counter += 1
        if month == 12:
            current_sim_date = current_sim_date.replace(year=year + 1, month=1)
        else:
            current_sim_date = current_sim_date.replace(month=month + 1)
        
        if all(d['current_balance'] <= 0 for d in live_debt_accounts.values()):
            print("\nAll active debts paid off before end of simulation period!")
            break

    # Final reporting outside the loop
    print(f"\n--- Debt Simulation Summary (as of {current_sim_date.strftime('%Y-%m-%d') if simulation_months_counter < 120 else 'End of 10-year cap'}) ---")
    all_paid_off_final = True
    for debt_name, debt_data in live_debt_accounts.items():
        if debt_data['current_balance'] > 0:
            print(f"  - {debt_name}: Remaining Balance: ${debt_data['current_balance']:.2f}")
            all_paid_off_final = False
        else:
            print(f"  - {debt_name}: Paid off!")
    
    if all_paid_off_final:
        print("All debts successfully paid off within the planning period!")
    else:
        print("Some debts remain outstanding at the end of the planning period.")

    return live_debt_accounts


def generate_spreadsheet_output(final_pay_periods, debt_progress_report):
    """
    Generates an Excel spreadsheet with the financial plan and debt progress, including charts.
    """
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'financial_plan.xlsx')

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book

        # --- Sheet 1: Paycheck Summary (High-Level) ---
        paycheck_summary_data = []
        for pp in final_pay_periods:
            row = {
                'Pay Date': pp['pay_date'].strftime('%Y-%m-%d'),
                'Net Pay': pp['net_pay'],
                'Initial Balance for Period': pp['initial_balance_for_period'],
                'Remaining Balance': pp['remaining_balance']
            }
            assigned_bills_str = "; ".join([
                f"{b['name']} (Due: {b['due_date'].strftime('%m-%d')}) - ${b['amount']:.2f}"
                for b in pp['assigned_bills']
            ])
            row['Assigned Bills'] = assigned_bills_str
            paycheck_summary_data.append(row)
        
        df_paychecks_summary = pd.DataFrame(paycheck_summary_data)
        df_paychecks_summary.to_excel(writer, sheet_name='Paycheck Summary', index=False)


        # --- Sheet 2: Paycheck Details (For Charting and Granular View) ---
        paycheck_details_data = []
        for pp in final_pay_periods:
            if pp['assigned_bills']:
                for bill in pp['assigned_bills']:
                    paycheck_details_data.append({
                        'Pay Date': pp['pay_date'].strftime('%Y-%m-%d'),
                        'Bill Name': bill['name'],
                        'Bill Due Date': bill['due_date'].strftime('%Y-%m-%d'),
                        'Amount Assigned': bill['amount'],
                        'Category': bill['category'] # Added category for potential future use or charting by category
                    })
            # Add remaining balance as a "bill" for charting purposes if desired
            paycheck_details_data.append({
                'Pay Date': pp['pay_date'].strftime('%Y-%m-%d'),
                'Bill Name': 'Remaining Balance',
                'Bill Due Date': '', # N/A for remaining balance
                'Amount Assigned': pp['remaining_balance'],
                'Category': 'Savings/Buffer' # Categorize remaining balance
            })
        
        df_paycheck_details = pd.DataFrame(paycheck_details_data)
        df_paycheck_details.to_excel(writer, sheet_name='Paycheck Details', index=False)

        # --- Sheet 3: Debt Progress ---
        if debt_progress_report:
            all_debt_history = []
            for debt_name, debt_data in debt_progress_report.items():
                for month_snapshot in debt_data['history']:
                    row = {
                        'Debt Name': debt_name,
                        'Date': month_snapshot['date'].strftime('%Y-%m-%d'),
                        'Balance Start of Month': month_snapshot['balance_start_of_month'],
                        'Total Fees Charged': month_snapshot['total_fees_charged'],
                        'Payments Made': month_snapshot['payments_made'],
                        'Interest Accrued': month_snapshot['interest_accrued'],
                        'Principal Paid': month_snapshot['principal_paid'],
                        'Balance End of Month': month_snapshot['balance_end_of_month']
                    }
                    all_debt_history.append(row)
            
            if all_debt_history:
                df_debt_progress = pd.DataFrame(all_debt_history)
                df_debt_progress.to_excel(writer, sheet_name='Debt Progress', index=False)
            else:
                print("No debt history to write to spreadsheet.")
        else:
            print("No debt progress report available to write to spreadsheet.")


        # --- Sheet 4: Paycheck Overview Chart (using data from Paycheck Details) ---
        # Prepare data for the chart by pivoting the paycheck details
        # This will create columns for each unique Bill Name
        df_chart_data = df_paycheck_details.pivot_table(
            index='Pay Date',
            columns='Bill Name',
            values='Amount Assigned',
            aggfunc='sum'
        ).fillna(0) # Fill NaN for bills not present in a given paycheck

        # Sort columns to ensure 'Remaining Balance' is typically last for better stacked chart visual
        # Get all bill names except 'Remaining Balance'
        bill_columns = [col for col in df_chart_data.columns if col != 'Remaining Balance']
        # Reorder columns: bill names first, then 'Remaining Balance'
        ordered_columns = bill_columns + ['Remaining Balance']
        df_chart_data = df_chart_data[ordered_columns]


        # Write the pivoted data to a new sheet for the chart
        # This sheet can be hidden or used as the source for the chart tab
        df_chart_data.to_excel(writer, sheet_name='Chart Data', index=True) # index=True to keep 'Pay Date' as a column

        # Get the worksheet object for the Chart Data sheet
        worksheet_chart_data = writer.sheets['Chart Data']

        # Create a new chart object.
        chart = workbook.add_chart({'type': 'column'})

        # Configure the chart series.
        # Data is in 'Chart Data' sheet. Headers are in row 1, data starts from row 2.
        num_paychecks = len(df_chart_data)
        num_bill_types = len(df_chart_data.columns) # Number of columns in df_chart_data

        # Category axis (Pay Dates)
        chart.set_x_axis({'name': 'Paycheck Date'})
        chart.set_y_axis({'name': 'Amount ($)', 'num_format': '$#,##0'})

        # Add series for each bill name and Remaining Balance
        # Loop through columns of df_chart_data (starting from the second column as the first is 'Pay Date')
        for i, col_name in enumerate(df_chart_data.columns):
            chart.add_series({
                'name':       ['Chart Data', 0, i + 1], # Sheet name, row 0 (header), column index + 1 (A=0, B=1, C=2...)
                'categories': ['Chart Data', 1, 0, num_paychecks, 0], # Sheet name, first data row (1), col 0 (Pay Date), last data row, col 0
                'values':     ['Chart Data', 1, i + 1, num_paychecks, i + 1], # Sheet name, first data row (1), col index + 1, last data row, col index + 1
                'data_labels': {'value': True, 'num_format': '$#,##0'}, # Add data labels for clarity
            })

        # Set chart title
        chart.set_title({'name': 'Paycheck Expense Breakdown'})
        
        # Set the chart to be a stacked column chart
        chart.set_plotarea({'area': {'fill': {'none': True}}}) # Remove plot area background
        chart.set_chartarea({'border': {'none': True}}) # Remove chart area border
        
        # Hide the legend for now if too many items, or put it at bottom
        chart.set_legend({'position': 'bottom'})


        # Insert the chart into a new sheet called 'Paycheck Chart'
        chart_sheet = workbook.add_worksheet('Paycheck Chart')
        chart_sheet.insert_chart('A1', chart) # Insert the chart at cell A1


    print(f"\nSpreadsheet generated successfully at: {output_file}")


def main_menu():
    """
    Main menu function for the MonteBuster Debt Simulator.
    Allows user to manage bills, run simulations, and generate reports.
    """
    bills = load_bills() # Load existing bill templates

    while True:
        print("\n--- MonteBuster Main Menu ---")
        print("1. Add a new bill")
        print("2. View/Edit bills") # Updated menu option
        print("3. Run Financial Plan Simulation")
        print("4. Exit")

        choice = get_user_input("Enter your choice: ").strip()

        if choice == '1':
            new_bill = add_bill()
            bills.append(new_bill)
            save_bills(bills)
            print(f"Bill '{new_bill['name']}' added successfully.")
        elif choice == '2':
            # Sub-menu for View/Edit
            while True:
                print("\n--- View/Edit Bills Menu ---")
                print("1. View all bills")
                print("2. Edit a bill")
                print("0. Back to Main Menu")
                edit_choice = get_user_input("Enter your choice: ").strip()

                if edit_choice == '1':
                    view_bills(bills)
                elif edit_choice == '2':
                    edit_bill(bills)
                elif edit_choice == '0':
                    break # Exit sub-menu
                else:
                    print("Invalid choice. Please try again.")
        elif choice == '3':
            if not bills:
                print("No bills loaded. Please add some bills first.")
                continue

            print("\n--- Financial Plan Simulation Setup ---")
            # Corrected example for bi-weekly paychecks in a year
            num_paychecks_str = get_user_input("Enter number of paychecks to simulate (e.g., 26 for a year, if bi-weekly): ").strip()
            try:
                num_paychecks = int(num_paychecks_str)
                if num_paychecks <= 0:
                    print("Number of paychecks must be positive.")
                    continue
            except ValueError:
                print("Invalid input. Please enter an integer.")
                continue

            net_pay_str = get_user_input("Enter your net pay per paycheck: $").strip().replace('$', '')
            try:
                net_pay = float(net_pay_str)
                if net_pay < 0:
                    print("Net pay cannot be negative.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a numerical value.")
                continue

            start_date_input = get_user_date_input("Enter the date of your first paycheck (YYYY-MM-DD): ")

            # Generate bill instances for the simulation period
            # Need to define an end_date for generate_bill_instances
            # Let's make it cover the period of the paychecks plus a buffer
            simulation_end_date = start_date_input + timedelta(weeks=2 * num_paychecks) + timedelta(days=31)
            bill_instances = generate_bill_instances(bills, start_date_input, simulation_end_date)
            
            # Filter debt templates to pass to simulate_debt_progress
            debt_templates = [b for b in bills if b.get('is_debt', False)]

            # Assign bills to paychecks
            final_pay_periods = assign_bills_to_paychecks(bill_instances, num_paychecks, net_pay, start_date_input)
            
            # Display summary
            display_paycheck_summary(final_pay_periods)

            # Simulate debt progress
            debt_progress_report = simulate_debt_progress(debt_templates, final_pay_periods)

            # Generate spreadsheet
            generate_spreadsheet_output(final_pay_periods, debt_progress_report)

        elif choice == '4':
            print("Exiting MonteBuster. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
