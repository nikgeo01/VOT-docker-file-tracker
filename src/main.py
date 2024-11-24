from tracker.activity_tracker import ActivityTracker

from utils.path_utils import set_yearly_files_path

# Set the yearly files path manually


if __name__ == '__main__':
    set_yearly_files_path('D:\porgramingOutOfCloud\VOT-docker-file-tracker\db')  # Replace with your desired path
    tracker = ActivityTracker()
    tracker.run()
