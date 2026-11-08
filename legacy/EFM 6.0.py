
BASE_DIR = os.environ.get("EFM_BASE_DIR", os.path.expanduser("~/Documents/EFM_Projects"))

import os
import shutil
import subprocess  # For opening the project folder
from datetime import datetime

def create_project_subfolders(project_path):
    """Creates the default subfolders and files within a new project folder."""
    subfolders = ['Exported', 'Project File', 'Files/Raw', 'Files/Stock', 'Files/Reference']
    for subfolder in subfolders:
        os.makedirs(os.path.join(project_path, subfolder), exist_ok=True)
    
    concept_file_path = os.path.join(project_path, 'Files', 'Concept.txt')
    with open(concept_file_path, 'w') as f:
        f.write("Concept Ideas and Notes:\n")
    
    sorting_folders = ['Image', 'Video', 'Audio', 'Doc']
    for folder in ['Raw', 'Stock']:
        for sorting_folder in sorting_folders:
            os.makedirs(os.path.join(project_path, 'Files', folder, sorting_folder), exist_ok=True)
    
    print(f"Subfolders and 'Concept.txt' created in '{project_path}'")

def open_folder(path):
    """Opens the folder in the default file explorer."""
    try:
        if os.name == 'nt':  # For Windows
            subprocess.Popen(['explorer', os.path.realpath(path)])
        elif os.name == 'posix':  # For MacOS/Linux
            subprocess.Popen(['open', path])
    except Exception as e:
        print(f"Failed to open folder: {e}")

def sort_files_into_subfolders(folder_path):
    """Sorts files in the specified folder into 'Image', 'Video', 'Audio', and 'Doc' subfolders."""
    extensions = {
        'Image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'Video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
        'Doc': ['.pdf', '.docx', '.txt', '.pptx', '.xlsx']
    }
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1].lower()
            
            for category, exts in extensions.items():
                if file_ext in exts:
                    destination_folder = os.path.join(folder_path, category)
                    os.makedirs(destination_folder, exist_ok=True)
                    shutil.move(file_path, destination_folder)
                    print(f"Moved '{filename}' to '{destination_folder}'")
                    break

def list_ongoing_projects():
    """Lists all ongoing project folders under the 'Client Project' and 'Personal Project' ongoing directories."""
    ongoing_projects = []
    
    client_ongoing = os.path.join(BASE_DIR, 'Client Project', 'Ongoing Project')
    personal_ongoing = os.path.join(BASE_DIR, 'Personal Project', 'Ongoing Project')
    
    for project_dir in [client_ongoing, personal_ongoing]:
        if os.path.exists(project_dir):
            for name in os.listdir(project_dir):
                project_path = os.path.join(project_dir, name)
                if os.path.isdir(project_path):
                    ongoing_projects.append(project_path)
    
    return ongoing_projects

def add_new_project(project_name=None):
    """Adds a new project to the appropriate ongoing project folder and initializes the folder structure."""
    if not project_name:
        project_name = input("Enter the name of the new project: ").strip()
        if not project_name:
            print("Project name cannot be empty.")
            return
    
    print("Is this a client project?")
    is_client_project_input = input("1. Yes\n2. No\nChoose an option: ").strip()
    if is_client_project_input == "1":
        is_client_project = True
    elif is_client_project_input == "2":
        is_client_project = False
    else:
        # If input is neither "1" nor "2", treat it as an invalid response and default to 'No'
        print("Invalid option. Defaulting to 'No'.")
        is_client_project = False
    
    date_str = datetime.now().strftime('%Y%m%d')
    project_folder_name = f"{project_name}_{date_str}"
    
    if is_client_project:
        path = os.path.join(BASE_DIR, 'Client Project', 'Ongoing Project', project_folder_name)
    else:
        path = os.path.join(BASE_DIR, 'Personal Project', 'Ongoing Project', project_folder_name)
    
    try:
        os.makedirs(path, exist_ok=True)
        create_project_subfolders(path)
        open_folder(path)
        print(f"New project '{project_name}' created at '{path}'")
    except Exception as e:
        print(f"Failed to create project: {e}")

def move_project():
    """Moves an existing project to the 'finished' or 'ignored' folder."""
    ongoing_projects = list_ongoing_projects()
    
    if not ongoing_projects:
        print("No ongoing projects found.")
        return
    
    print("Ongoing Projects:")
    for idx, project in enumerate(ongoing_projects):
        print(f"{idx + 1}. {os.path.basename(project)}")
    
    choice_input = input("Select a project to move (enter the number): ").strip()
    if not choice_input.isdigit():
        print("Invalid input. Please enter a number corresponding to the project.")
        return
    choice = int(choice_input) - 1
    if choice < 0 or choice >= len(ongoing_projects):
        print("Invalid selection.")
        return
    
    project_folder_path = ongoing_projects[choice]
    is_client_project = 'Client Project' in project_folder_path
    
    print("Is the project finished or ignored?")
    status_input = input("1. Finished\n2. Ignored\n3. learning\nChoose an option: ").strip()
    if status_input == "1":
        status = 'finished'
    elif status_input == "2":
        status = 'ignored'
    elif status_input == "3":
        status = 'learning'
    else:
        print("Invalid option.")
        return
    
    client_type = None
    project_type = None
    rebound_folder = None  # Initialize to None to avoid UnboundLocalError
    
    if is_client_project and status == 'finished':
        print("Is it a Project Based or Rebound client?")
        client_type_input = input("1. Project Based\n2. Rebound\nChoose an option: ").strip()
        
        if client_type_input == "1":
            client_type = 'project'
            print("Enter the project type:")
            project_type_input = input("1. Animation\n2. Video Editing\n3. Image Editing\n4. Graphics Design\n5. Whole Package\nChoose an option: ").strip()
            
            project_type_map = {
                "1": 'Animation',
                "2": 'Video Editing',
                "3": 'Image Editing',
                "4": 'Graphics Design',
                "5": 'Whole Package'
            }
            project_type = project_type_map.get(project_type_input)
            if not project_type:
                print("Invalid project type.")
                return
        elif client_type_input == "2":
            client_type = 'rebound'
            print("1. Create a new folder\n2. Select an existing folder")
            folder_choice_input = input("Choose an option: ").strip()
            if folder_choice_input == "1":
                rebound_folder = input("Enter the new folder name for the rebound client: ").strip()
                if not rebound_folder:
                    print("Folder name cannot be empty.")
                    return
            elif folder_choice_input == "2":
                rebound_clients_path = os.path.join(BASE_DIR, 'Client Project', 'Finished Project', 'Rebound Clients')
                if not os.path.exists(rebound_clients_path):
                    os.makedirs(rebound_clients_path, exist_ok=True)
                existing_folders = [f for f in os.listdir(rebound_clients_path) if os.path.isdir(os.path.join(rebound_clients_path, f))]
                if not existing_folders:
                    print("No existing folders found. Creating a new folder.")
                    rebound_folder = input("Enter the new folder name for the rebound client: ").strip()
                    if not rebound_folder:
                        print("Folder name cannot be empty.")
                        return
                else:
                    print("Existing Folders:")
                    for idx, folder in enumerate(existing_folders):
                        print(f"{idx + 1}. {folder}")
                    selected_folder_input = input("Select an existing folder (enter the number): ").strip()
                    if not selected_folder_input.isdigit():
                        print("Invalid input.")
                        return
                    selected_folder_idx = int(selected_folder_input) - 1
                    if selected_folder_idx < 0 or selected_folder_idx >= len(existing_folders):
                        print("Invalid selection.")
                        return
                    rebound_folder = existing_folders[selected_folder_idx]
            else:
                print("Invalid option.")
                return
        else:
            print("Invalid client type.")
            return
    
    move_project_logic(project_folder_path, is_client_project, status, client_type, project_type, rebound_folder)

def move_project_logic(project_folder_path, is_client_project, status, client_type=None, project_type=None, rebound_folder=None):
    """Handles the logic for moving a project to the appropriate location."""
    project_name = os.path.basename(project_folder_path)
    
    try:
        if is_client_project:
            if status == 'finished':
                if client_type == 'project':
                    if project_type:
                        destination = os.path.join(BASE_DIR, 'Client Project', 'Finished Project', 'Project Based Clients', project_type)
                    else:
                        print("Project type is required for Project Based clients.")
                        return
                elif client_type == 'rebound':
                    if rebound_folder:
                        destination = os.path.join(BASE_DIR, 'Client Project', 'Finished Project', 'Rebound Clients', rebound_folder)
                        os.makedirs(destination, exist_ok=True)
                    else:
                        print("Rebound folder is required for Rebound clients.")
                        return
                else:
                    print("Invalid client type specified.")
                    return
            elif status == 'ignored':
                destination = os.path.join(BASE_DIR, 'Client Project', 'Ignored Project')
            elif status == 'learning':
                destination = os.path.join(BASE_DIR, 'Client Project', 'Learning Project')
            else:
                print("Invalid status specified.")
                return
        else:
            if status == 'finished':
                destination = os.path.join(BASE_DIR, 'Personal Project', 'Finished Project')
            elif status == 'ignored':
                destination = os.path.join(BASE_DIR, 'Personal Project', 'Ignored Project')
            elif status == 'learning':
                destination = os.path.join(BASE_DIR, 'Personal Project', 'Learning Project')
            else:
                print("Invalid status specified.")
                return
        
        # Ensure the destination directory exists
        os.makedirs(destination, exist_ok=True)
        
        # Move the project
        shutil.move(project_folder_path, destination)
        open_folder(destination)
        print(f"Moved project '{project_name}' to '{destination}'")
    except Exception as e:
        print(f"Failed to move project: {e}")

def main():
    user_input = input("What would you like to do?\n1. Create a new project\n2. Move an existing project\n3. Open Projects\nChoose an option: ").strip()
    
    if user_input == "1":
        add_new_project()
    elif user_input == "2":
        move_project()
    elif user_input == "3":
        ongoing_projects = list_ongoing_projects()
        if not ongoing_projects:
            print("No ongoing projects found.")
            return
        print("Ongoing Projects:")
        for idx, project in enumerate(ongoing_projects):
            print(f"{idx + 1}. {os.path.basename(project)}")
        choice_input = input("Select a project to open (enter the number): ").strip()
        if not choice_input.isdigit():
            print("Invalid input. Please enter a valid number.")
            return
        choice = int(choice_input) - 1
        if choice < 0 or choice >= len(ongoing_projects):
            print("Invalid selection.")
            return
        selected_project = ongoing_projects[choice]
        open_folder(selected_project)
        # Sort files in 'Files/Raw' and 'Files/Stock' directories
        raw_path = os.path.join(selected_project, 'Files', 'Raw')
        stock_path = os.path.join(selected_project, 'Files', 'Stock')
        if os.path.exists(raw_path):
            sort_files_into_subfolders(raw_path)
        if os.path.exists(stock_path):
            sort_files_into_subfolders(stock_path)
    elif user_input and user_input not in ["1", "2", "3"]:
        # Treat any other input as a new project name
        add_new_project(project_name=user_input)
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()
