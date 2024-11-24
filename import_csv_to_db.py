import os
import csv
import logging
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# ================================
# Configuration and Setup
# ================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Database URL (ensure it's set correctly)
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/file_usage_tracker'
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# ================================
# SQLAlchemy Model Definition
# ================================

class UserActivity(Base):
    """
    SQLAlchemy model for the 'user_activities' table.
    """
    __tablename__ = 'user_activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    date_and_hour = Column(DateTime, nullable=False)
    file_worked_on = Column(String, nullable=True)
    time_spent_seconds = Column(Float, default=0.0)
    app_used = Column(String, nullable=True)
    project_name = Column(String, nullable=True)

    def __repr__(self):
        return (f"<UserActivity(id={self.id}, user_name='{self.user_name}', "
                f"date_and_hour='{self.date_and_hour}')>")

# ================================
# CSV Import Function
# ================================

def import_csv_files():
    """
    Imports user activity data from CSV files located in the 'db' directory
    into the PostgreSQL database.
    """
    db_folder = 'db'  # Folder where CSV files are located

    # Check if the database folder exists
    if not os.path.isdir(db_folder):
        logging.error(f"Database folder '{db_folder}' does not exist.")
        return

    # Iterate over all CSV files in the directory
    try:
        for filename in os.listdir(db_folder):
            if filename.lower().endswith('.csv'):
                filepath = os.path.join(db_folder, filename)
                logging.info(f"Importing {filepath}...")

                with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    activities = []  # List to hold UserActivity instances

                    for row_number, row in enumerate(reader, start=1):
                        try:
                            # Extract user_name from the row or filename
                            user_name = row.get('User Name') or row.get('user_name')
                            if not user_name:
                                filename_without_ext = os.path.splitext(filename)[0]
                                parts = filename_without_ext.split('_')
                                user_name = parts[0] if parts else 'Unknown'

                            # Parse the date and time
                            date_and_hour_str = row.get('Date and Hour')
                            if date_and_hour_str:
                                date_and_hour = datetime.strptime(
                                    date_and_hour_str, '%Y-%m-%d %H:%M'
                                )
                            else:
                                logging.warning(
                                    f"Skipping row {row_number} in {filename} due to missing date: {row}"
                                )
                                continue  # Skip this row

                            # Parse time spent seconds, handle possible conversion errors
                            time_spent_str = row.get('Time Spent on File (seconds)', '0')
                            try:
                                time_spent_seconds = float(time_spent_str)
                            except ValueError:
                                logging.warning(
                                    f"Invalid time spent value on row {row_number} in {filename}: '{time_spent_str}'. Setting to 0."
                                )
                                time_spent_seconds = 0.0

                            # Create the UserActivity instance
                            activity = UserActivity(
                                user_name=user_name,
                                date_and_hour=date_and_hour,
                                file_worked_on=row.get('File Worked On', ''),
                                time_spent_seconds=time_spent_seconds,
                                app_used=row.get('App Used', ''),
                                project_name=row.get('Project Name', '')
                            )
                            activities.append(activity)

                        except Exception as e:
                            logging.error(
                                f"Failed to import row {row_number} in {filename}: {e}"
                            )
                            logging.debug(f"Row data: {row}")

                    # Bulk insert all activities for the current CSV file
                    if activities:
                        with Session() as session:
                            session.bulk_save_objects(activities)
                            session.commit()
                            logging.info(
                                f"Successfully imported {len(activities)} records from {filename}."
                            )
                    else:
                        logging.info(f"No valid records found in {filename} to import.")

        logging.info("Data import completed successfully.")

    except Exception as e:
        logging.error(f"Failed to import CSV files: {e}")

# ================================
# Main Execution
# ================================

def main():
    """
    Main function to set up the database and initiate CSV import.
    """
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        logging.info("Database tables created or verified successfully.")

        # Import CSV files
        import_csv_files()

    except Exception as e:
        logging.error(f"An error occurred during setup or import: {e}")

if __name__ == "__main__":
    main()
