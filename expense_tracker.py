import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

def create_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def add_expense():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- Add New Expense ---")
    
    try:
        amount = float(input("Enter amount: $"))
        category = input("Enter category (e.g., Food, Transport, Entertainment): ").strip()
        description = input("Enter description: ").strip()
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO expenses (date, amount, category, description)
            VALUES (?, ?, ?, ?)
        ''', (current_date, amount, category, description))
        
        conn.commit()
        print("Expense added successfully!")
    except ValueError:
        print("Invalid amount! Please enter a number.")
    finally:
        conn.close()

def view_all_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- All Expenses ---")
    
    cursor.execute('''
        SELECT * FROM expenses 
        ORDER BY date DESC
    ''')
    
    expenses = cursor.fetchall()
    
    if not expenses:
        print("No expenses found!")
        return
    
    print(f"{'ID':<5} {'Date':<12} {'Amount':<10} {'Category':<15} {'Description'}")
    print("-" * 60)
    
    total = 0
    for expense in expenses:
        expense_id, date, amount, category, description = expense
        print(f"{expense_id:<5} {date:<12} ${amount:<9.2f} {category:<15} {description}")
        total += amount
    
    print("-" * 60)
    print(f"{'TOTAL':<5} {'':<12} ${total:<9.2f}")
    
    conn.close()

# NEW FEATURE 1: Edit Expenses
def edit_expense():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- Edit Expense ---")
    view_all_expenses()
    
    try:
        expense_id = int(input("\nEnter the ID of the expense you want to edit: "))
        
        # Check if expense exists
        cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        expense = cursor.fetchone()
        
        if not expense:
            print("Expense ID not found!")
            return
        
        print(f"\nEditing Expense: {expense}")
        
        print("\nLeave blank to keep current value:")
        new_amount = input(f"New amount [current: ${expense[2]}]: ")
        new_category = input(f"New category [current: {expense[3]}]: ")
        new_description = input(f"New description [current: {expense[4]}]: ")
        
        # Update only provided fields
        update_fields = []
        update_values = []
        
        if new_amount:
            update_fields.append("amount = ?")
            update_values.append(float(new_amount))
        if new_category:
            update_fields.append("category = ?")
            update_values.append(new_category)
        if new_description:
            update_fields.append("description = ?")
            update_values.append(new_description)
        
        if update_fields:
            update_values.append(expense_id)
            update_query = f"UPDATE expenses SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(update_query, update_values)
            conn.commit()
            print("Expense updated successfully!")
        else:
            print("No changes made.")
            
    except ValueError:
        print("Please enter a valid ID number.")
    finally:
        conn.close()

# NEW FEATURE 2: Delete Expenses
def delete_expense():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- Delete Expense ---")
    view_all_expenses()
    
    try:
        expense_id = int(input("\nEnter the ID of the expense you want to delete: "))
        
        # Confirm deletion
        confirm = input("Are you sure you want to delete this expense? (y/n): ").lower()
        if confirm == 'y':
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("Expense deleted successfully!")
            else:
                print("Expense ID not found!")
        else:
            print("Deletion cancelled.")
            
    except ValueError:
        print("Please enter a valid ID number.")
    finally:
        conn.close()

# NEW FEATURE 3: Monthly Spending Reports
def monthly_report():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- Monthly Spending Report ---")
    
    # Get current year and month
    current_year = datetime.now().year
    year = input(f"Enter year for report [default: {current_year}]: ") or str(current_year)
    month = input("Enter month (01-12) [default: current month]: ") or datetime.now().strftime("%m")
    
    try:
        # Get monthly total
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ''', (year, month))
        
        monthly_total = cursor.fetchone()[0] or 0
        
        # Get category breakdown
        cursor.execute('''
            SELECT category, SUM(amount) as total 
            FROM expenses 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY category 
            ORDER BY total DESC
        ''', (year, month))
        
        categories = cursor.fetchall()
        
        month_name = datetime.strptime(month, "%m").strftime("%B")
        print(f"\nMonthly Report for {month_name} {year}")
        print("=" * 40)
        print(f"Total Spending: ${monthly_total:.2f}")
        print("\nBreakdown by Category:")
        print("-" * 30)
        
        for category, total in categories:
            percentage = (total / monthly_total) * 100 if monthly_total > 0 else 0
            print(f"{category:<15} ${total:>8.2f} ({percentage:>5.1f}%)")
            
    except Exception as e:
        print(f"Error generating report: {e}")
    finally:
        conn.close()

# NEW FEATURE 4: Data Visualization with Charts
def visualize_data():
    try:
        conn = sqlite3.connect('expenses.db')
        
        # Load data into pandas DataFrame
        df = pd.read_sql_query('''
            SELECT date, amount, category 
            FROM expenses 
            ORDER BY date
        ''', conn)
        
        if df.empty:
            print("No data available for visualization!")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        print("\n--- Data Visualization ---")
        print("1. Category Pie Chart")
        print("2. Monthly Spending Trend")
        print("3. Back to Main Menu")
        
        choice = input("Choose visualization (1-3): ")
        
        if choice == '1':
            # Pie chart by category
            category_totals = df.groupby('category')['amount'].sum()
            
            plt.figure(figsize=(10, 8))
            plt.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%', startangle=90)
            plt.title('Spending by Category')
            plt.show()
            
        elif choice == '2':
            # Monthly trend line chart
            monthly_totals = df.groupby('month')['amount'].sum()
            
            plt.figure(figsize=(12, 6))
            monthly_totals.plot(kind='line', marker='o')
            plt.title('Monthly Spending Trend')
            plt.xlabel('Month')
            plt.ylabel('Amount ($)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
            
        elif choice == '3':
            return
        else:
            print("Invalid choice!")
            
    except ImportError:
        print("Visualization features require matplotlib and pandas.")
        print("Install them using: pip install matplotlib pandas")
    except Exception as e:
        print(f"Error generating visualization: {e}")
    finally:
        conn.close()

def view_category_summary():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("\n--- Spending by Category ---")
    
    cursor.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        GROUP BY category 
        ORDER BY total DESC
    ''')
    
    categories = cursor.fetchall()
    
    if not categories:
        print("No expenses found!")
        return
    
    total_spent = 0
    print(f"{'Category':<15} {'Total Amount'}")
    print("-" * 30)
    
    for category, total in categories:
        print(f"{category:<15} ${total:.2f}")
        total_spent += total
    
    print("-" * 30)
    print(f"{'TOTAL':<15} ${total_spent:.2f}")
    
    conn.close()

def main_menu():
    while True:
        print("\n" + "="*50)
        print("           ENHANCED EXPENSE TRACKER")
        print("="*50)
        print("1. Add New Expense")
        print("2. View All Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. View Category Summary")
        print("6. Monthly Spending Report")
        print("7. Data Visualization")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            add_expense()
        elif choice == '2':
            view_all_expenses()
        elif choice == '3':
            edit_expense()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            view_category_summary()
        elif choice == '6':
            monthly_report()
        elif choice == '7':
            visualize_data()
        elif choice == '8':
            print("Thank you for using Enhanced Expense Tracker! Goodbye!")
            break
        else:
            print("Invalid choice! Please enter 1-8.")

# Start the program
if __name__ == "__main__":
    create_database()
    main_menu()