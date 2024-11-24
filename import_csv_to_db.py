import os
import csv
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Database URL (ensure it's set correctly)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/file_usage_tracker')

# Create the database engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the database models (UserActivity class as before)

def import_csv_files():
    session = Session()
    db_folder = 'db'  # Folder where CSV files are located
    try:
        for filename in os.listdir(db_folder):
            if filename.endswith('.csv'):
                filepath = os.path.join(db_folder, filename)
                print(f"Importing {filepath}...")
                with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            # Get the user_name from the row or filename
                            user_name = row.get('User Name') or row.get('user_name')
                            if not user_name:
                                filename_without_ext = os.path.splitext(filename)[0]
                                parts = filename_without_ext.split('_')
                                if len(parts) > 0:
                                    user_name = parts[0]
                                else:
                                    user_name = 'Unknown'

                            # Parse the date and time
                            date_and_hour_str = row.get('Date and Hour')
                            if date_and_hour_str:
                                date_and_hour = datetime.strptime(date_and_hour_str, '%Y-%m-%d %H:%M')
                            else:
                                print(f"Skipping row due to missing date: {row}")
                                continue  # Skip this row

                            # Create the UserActivity instance
                            activity = UserActivity(
                                user_name=user_name,
                                date_and_hour=date_and_hour,
                                file_worked_on=row.get('File Worked On', ''),
                                time_spent_seconds=float(row.get('Time Spent on File (seconds)', '0')),
                                app_used=row.get('App Used', ''),
                                project_name=row.get('Project Name', '')
                            )
                            session.add(activity)
                        except Exception as e:
                            print(f"Failed to import row: {e}")
                            print(f"Row data: {row}")
                    session.commit()
        print("Data import completed successfully.")
    except Exception as e:
        print(f"Failed to import CSV files: {e}")
        session.rollback()
    finally:
        session.close()
