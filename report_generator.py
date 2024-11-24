import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
import csv

# Load environment variable for DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/file_usage_tracker')

# Create the database engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the database model
class UserActivity(Base):
    __tablename__ = 'user_activity'
    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    date_and_hour = Column(DateTime)
    file_worked_on = Column(String)
    time_spent_seconds = Column(Float)
    app_used = Column(String)
    project_name = Column(String)

# Function to generate the project report
def generate_project_report(project_name, output_file):
    session = Session()
    try:
        # Query total time spent by each user on the project
        results = session.query(
            UserActivity.user_name,
            func.sum(UserActivity.time_spent_seconds).label('total_time')
        ).filter(UserActivity.project_name == project_name).group_by(UserActivity.user_name).all()

        if not results:
            messagebox.showinfo("No Data", f"No data found for project '{project_name}'.")
            return

        total_time_spent = sum([row.total_time for row in results])

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'User Name',
                'Total Time Spent on Project (seconds)',
                'Total Time Spent by All Users (seconds)'
            ]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for row in results:
                writer.writerow([row.user_name, row.total_time, total_time_spent])
            # Add a total row at the end
            writer.writerow(['Total', total_time_spent, total_time_spent])

        messagebox.showinfo("Success", f"Project report generated successfully at:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate project report.\nError: {e}")
    finally:
        session.close()

# Function to generate the user activity report
def generate_user_activity_report(user_name, start_date, end_date, output_file):
    session = Session()
    try:
        # Query user activity within the date range
        results = session.query(UserActivity).filter(
            UserActivity.user_name == user_name,
            UserActivity.date_and_hour >= start_date,
            UserActivity.date_and_hour <= end_date
        ).order_by(UserActivity.date_and_hour).all()

        if not results:
            messagebox.showinfo("No Data", f"No activity found for user '{user_name}' in the specified time period.")
            return

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date and Hour', 'File Worked On', 'Time Spent on File (seconds)', 'App Used', 'Project Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for activity in results:
                writer.writerow({
                    'Date and Hour': activity.date_and_hour.strftime('%Y-%m-%d %H:%M'),
                    'File Worked On': activity.file_worked_on or '-',
                    'Time Spent on File (seconds)': activity.time_spent_seconds or '0',
                    'App Used': activity.app_used or 'Unknown',
                    'Project Name': activity.project_name or '-'
                })

        messagebox.showinfo("Success", f"User activity report generated successfully at:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate user activity report.\nError: {e}")
    finally:
        session.close()

# Main application GUI
class ReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Report Generator")

        # Create tabs
        self.tab_control = ttk.Notebook(root)

        self.project_report_tab = ttk.Frame(self.tab_control)
        self.user_activity_report_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.project_report_tab, text='Project Report')
        self.tab_control.add(self.user_activity_report_tab, text='User Activity Report')

        self.tab_control.pack(expand=1, fill='both')

        self.create_project_report_tab()
        self.create_user_activity_report_tab()

    def create_project_report_tab(self):
        # Project Name
        ttk.Label(self.project_report_tab, text="Project Name:").grid(column=0, row=0, padx=10, pady=10, sticky='E')
        self.project_name_entry = ttk.Entry(self.project_report_tab, width=30)
        self.project_name_entry.grid(column=1, row=0, padx=10, pady=10)

        # Output File
        ttk.Label(self.project_report_tab, text="Output File:").grid(column=0, row=1, padx=10, pady=10, sticky='E')
        self.project_output_entry = ttk.Entry(self.project_report_tab, width=30)
        self.project_output_entry.grid(column=1, row=1, padx=10, pady=10)
        self.project_output_entry.insert(0, "project_report.csv")

        # Browse Button
        self.project_browse_button = ttk.Button(self.project_report_tab, text="Browse", command=self.browse_project_output)
        self.project_browse_button.grid(column=2, row=1, padx=10, pady=10)

        # Generate Button
        self.project_generate_button = ttk.Button(self.project_report_tab, text="Generate Report", command=self.generate_project_report_action)
        self.project_generate_button.grid(column=1, row=2, padx=10, pady=20)

    def create_user_activity_report_tab(self):
        # User Name
        ttk.Label(self.user_activity_report_tab, text="User Name:").grid(column=0, row=0, padx=10, pady=10, sticky='E')
        self.user_name_entry = ttk.Entry(self.user_activity_report_tab, width=30)
        self.user_name_entry.grid(column=1, row=0, padx=10, pady=10)

        # Start Date
        ttk.Label(self.user_activity_report_tab, text="Start Date (YYYY-MM-DD):").grid(column=0, row=1, padx=10, pady=10, sticky='E')
        self.start_date_entry = ttk.Entry(self.user_activity_report_tab, width=30)
        self.start_date_entry.grid(column=1, row=1, padx=10, pady=10)

        # End Date
        ttk.Label(self.user_activity_report_tab, text="End Date (YYYY-MM-DD):").grid(column=0, row=2, padx=10, pady=10, sticky='E')
        self.end_date_entry = ttk.Entry(self.user_activity_report_tab, width=30)
        self.end_date_entry.grid(column=1, row=2, padx=10, pady=10)

        # Output File
        ttk.Label(self.user_activity_report_tab, text="Output File:").grid(column=0, row=3, padx=10, pady=10, sticky='E')
        self.user_output_entry = ttk.Entry(self.user_activity_report_tab, width=30)
        self.user_output_entry.grid(column=1, row=3, padx=10, pady=10)
        self.user_output_entry.insert(0, "user_activity_report.csv")

        # Browse Button
        self.user_browse_button = ttk.Button(self.user_activity_report_tab, text="Browse", command=self.browse_user_output)
        self.user_browse_button.grid(column=2, row=3, padx=10, pady=10)

        # Generate Button
        self.user_generate_button = ttk.Button(self.user_activity_report_tab, text="Generate Report", command=self.generate_user_activity_report_action)
        self.user_generate_button.grid(column=1, row=4, padx=10, pady=20)

    def browse_project_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            self.project_output_entry.delete(0, tk.END)
            self.project_output_entry.insert(0, filename)

    def browse_user_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            self.user_output_entry.delete(0, tk.END)
            self.user_output_entry.insert(0, filename)

    def generate_project_report_action(self):
        project_name = self.project_name_entry.get().strip()
        output_file = self.project_output_entry.get().strip()

        if not project_name:
            messagebox.showerror("Input Error", "Please enter a project name.")
            return

        if not output_file:
            messagebox.showerror("Input Error", "Please specify an output file.")
            return

        generate_project_report(project_name, output_file)

    def generate_user_activity_report_action(self):
        user_name = self.user_name_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        output_file = self.user_output_entry.get().strip()

        if not user_name:
            messagebox.showerror("Input Error", "Please enter a user name.")
            return

        if not start_date_str or not end_date_str:
            messagebox.showerror("Input Error", "Please enter both start date and end date.")
            return

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Adjust end_date to include the entire day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        if not output_file:
            messagebox.showerror("Input Error", "Please specify an output file.")
            return

        generate_user_activity_report(user_name, start_date, end_date, output_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()
