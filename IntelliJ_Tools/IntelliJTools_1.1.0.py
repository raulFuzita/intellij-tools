import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Author: Raul Macedo Fuzita

class EclipseToIntelliJ(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Eclipse To IntelliJ")
        self.geometry("700x450")

        self.classpath_file = self.get_classpath_file()
        self.application_libraries = self.get_application_libraries_intellij()

        self.config_file = "intellij_settings.json"
        self.load_config()

        self.create_widgets()

    def get_classpath_file(self):
        return self.get_file_path_in_current_directory('.classpath')

    def get_application_libraries_intellij(self):
        # Get the computer username
        username = os.getlogin()  
        jetbrais_dir = f'C:/Users/{username}/AppData/Roaming/JetBrains/'

        idea_version = self.get_last_updated_folders(jetbrais_dir)

        return f'{jetbrais_dir}{idea_version}/options/applicationLibraries.xml'


    def get_last_updated_folders(self, directory):
        # Get the list of all folders in the provided directory
        folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
        
        # Get the last modified time for each folder
        folder_last_modified_times = [(folder, os.path.getmtime(os.path.join(directory, folder))) for folder in folders]
        
        # Find the maximum last modified time
        max_last_modified_time = max(folder_last_modified_times, key=lambda x: x[1])[1]
        
        # Get the list of folders that have the maximum last modified time
        last_updated_folders = [folder[0] for folder in folder_last_modified_times if folder[1] == max_last_modified_time]
        
        return last_updated_folders[0]
        

    def get_file_path_in_current_directory(self, filename):
        # Get the absolute path of the current Python file
        current_file_path = os.path.abspath(__file__)
        # Get the directory containing the current Python file
        current_directory = os.path.dirname(current_file_path)
        # Create the target file path using the directory and the filename
        target_file_path = os.path.join(current_directory, filename).capitalize()
        target_file_path = target_file_path.replace('\\', '/')

        return target_file_path

    def load_config(self):
        target_file_path = self.get_file_path_in_current_directory(self.config_file)
        if os.path.exists(target_file_path):
            with open(target_file_path, "r") as f:
                self.config_data = json.load(f)
        else:
            self.config_data = {}

    def save_config(self):
        target_file_path = self.get_file_path_in_current_directory(self.config_file)
        with open(target_file_path, "w") as f:
            json.dump(self.config_data, f, indent=4)

    def delete_settings_file(self):
        settings_file_path = self.get_file_path_in_current_directory("intellij_settings.json")
        if os.path.isfile(settings_file_path):
            os.remove(settings_file_path)
            self.reset_env_variable()
            self.reset_classpath()
            self.reset_application_libraries()
            messagebox.showinfo("Success", "Deleted intellij_settings.json")

    def reset_env_variable(self, default="JAVA_MODULE"):
        self.environment_variable_entry.delete(0, tk.END)
        self.environment_variable_entry.insert(0, default)

    def reset_classpath(self, default=""):
        if default.strip() == "":
            self.classpath_file = self.get_classpath_file()
        else:
            self.classpath_file = default
        self.classpath_file_entry.delete(0, tk.END)
        self.classpath_file_entry.insert(0, self.classpath_file)

    def reset_application_libraries(self, default=""):
        if default.strip() == "":
            self.application_libraries = self.get_application_libraries_intellij()
        else:
            self.application_libraries = default
        self.application_libraries_entry.delete(0, tk.END)
        self.application_libraries_entry.insert(0, self.application_libraries)

    def create_widgets(self):

        # Create a menu bar
        self.menubar = Menu(self)

        # Create the menu, add it to the menu bar
        self.menusettings = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=self.menusettings)
        # Add menu items with commands
        self.menusettings.add_command(label="Delete", command=self.delete_settings_file)
        # Configure the main app window to display the menu bar
        self.config(menu=self.menubar)

        # Environment variable
        self.environment_variable_label = tk.Label(self, text="Environment variable", anchor='w')
        self.environment_variable_label.pack(fill=tk.X, padx=20, pady=(10, 0))
        self.environment_variable_entry = tk.Entry(self)
        self.environment_variable_entry.pack(fill=tk.X, padx=20, pady=(5, 30), ipadx=20, ipady=5)
        self.environment_variable_entry.insert(0, self.config_data.get("environment_variable", "JAVA_MODULE"))

        # Root directory
        self.root_directory_label = tk.Label(self, text="Root directory", anchor='w')
        self.root_directory_label.pack(fill=tk.X, padx=20)
        self.root_directory_frame = tk.Frame(self)
        self.root_directory_frame.pack(fill=tk.X, padx=20, pady=(0, 30))
        self.root_directory_entry = tk.Entry(self.root_directory_frame)
        self.root_directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipadx=20, ipady=5)
        self.root_directory_button = tk.Button(self.root_directory_frame, text="Browse", command=self.browse_root_directory)
        self.root_directory_button.pack(side=tk.RIGHT, ipadx=20, ipady=5)
        self.root_directory_entry.insert(0, self.config_data.get("root_directory", ""))

        # Classpath file
        self.classpath_file_label = tk.Label(self, text="Classpath file", anchor='w')
        self.classpath_file_label.pack(fill=tk.X, padx=20)
        self.classpath_file_frame = tk.Frame(self)
        self.classpath_file_frame.pack(fill=tk.X, padx=20, pady=(0, 30))
        self.classpath_file_entry = tk.Entry(self.classpath_file_frame)
        self.classpath_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipadx=20, ipady=5)
        self.classpath_file_button = tk.Button(self.classpath_file_frame, text="Browse", command=self.browse_classpath_file)
        self.classpath_file_button.pack(side=tk.RIGHT, ipadx=20, ipady=5)
        self.classpath_file_entry.insert(0, self.config_data.get("classpath_file", self.classpath_file))

        # ApplicationLibraries file
        self.application_libraries_label = tk.Label(self, text="ApplicationLibraries file", anchor='w')
        self.application_libraries_label.pack(fill=tk.X, padx=20)
        self.application_libraries_frame = tk.Frame(self)
        self.application_libraries_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.application_libraries_entry = tk.Entry(self.application_libraries_frame)
        self.application_libraries_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipadx=20, ipady=5)
        self.application_libraries_button = tk.Button(self.application_libraries_frame, text="Browse", command=self.browse_application_libraries)
        self.application_libraries_button.pack(side=tk.RIGHT, ipadx=20, ipady=5)
        self.application_libraries_entry.insert(0, self.config_data.get("application_libraries_file", self.application_libraries))

        # Generate and Cancel buttons
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(side=tk.RIGHT, padx=(0, 20))

        self.cancel_button = tk.Button(self.buttons_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=5)

        self.generate_button = tk.Button(self.buttons_frame, text="Generate", command=self.generate)
        self.generate_button.pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def browse_root_directory(self):
        directory = filedialog.askdirectory()
        self.root_directory_entry.delete(0, tk.END)
        self.root_directory_entry.insert(0, directory)

    def browse_classpath_file(self):
        file = filedialog.askopenfilename()
        if file.strip() == "":
            self.reset_classpath(self.config_data.get("classpath_file", ""))
            return
        
        self.classpath_file_entry.delete(0, tk.END)
        self.classpath_file_entry.insert(0, file)

    def browse_application_libraries(self):
        directory = filedialog.askdirectory()
        if directory.strip() == "":
            self.reset_application_libraries(self.config_data.get("application_libraries_file", ""))
            return
        
        self.application_libraries_entry.delete(0, tk.END)
        self.application_libraries_entry.insert(0, directory + '/applicationLibraries.xml')

    def prettify_xml(self, elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def write_to_reportlog(self, content):
        output_log = self.get_file_path_in_current_directory('report.log')
        with open(output_log, 'a+', encoding='utf-8') as f:
                f.write(content)
    
    def generate_global_libraries(self):
        # Check if the output directory exists, otherwise use the current directory
        if not os.path.exists(self.application_libraries_file):
            self.application_libraries_file = self.get_file_path_in_current_directory('applicationLibraries.xml')

        if not os.path.exists(self.classpath_file):
            self.classpath_file = self.get_file_path_in_current_directory('.classpath')

        # Read the .classpath file
        with open(self.classpath_file, 'r') as f:
            classpath_content = f.read()

        # Extract jar paths from .classpath
        jar_paths = re.findall(r'path="(/Libs[^"]+\.jar)', classpath_content)

        # Create applicationLibraries.xml with the extracted jars
        root = ET.Element('application')
        component = ET.SubElement(root, 'component', {'name': 'libraryTable'})

        missing_jars = []

        for jar_path in jar_paths:
            full_jar_path = os.path.join(self.root_directory, jar_path[1:])
            
            # Check if the jar exists
            if os.path.exists(full_jar_path):
                library_name = jar_path.split('/')[-1].replace('.jar', '')
                library = ET.SubElement(component, 'library', {'name': library_name})

                classes = ET.SubElement(library, 'CLASSES')
                ET.SubElement(classes, 'root', {'url': f'jar://${self.environment_variable}$/{jar_path}!/'})
                
                ET.SubElement(library, 'JAVADOC')
                ET.SubElement(library, 'SOURCES')
            else:
                missing_jars.append(full_jar_path.replace('\\', '/'))

        # Write the indented XML to a file
        pretty_xml = self.prettify_xml(root)
        with open(self.application_libraries_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        # Write the missing jars to a report.log file
        if missing_jars:
            output_log = self.get_file_path_in_current_directory('report.log')
            with open(output_log, 'w', encoding='utf-8') as f:
                f.write('\n***** MISSING JARS *****\n')
                for missing_jar in missing_jars:
                    f.write(f'{missing_jar}\n')

    def generate_report(self):
        report = ('\n***** SETTINGS ***** \n' 
                    f'Environment variable: {self.environment_variable}\n'
                    f'Root directory: {self.root_directory}\n'
                    f'Classpath file: {self.classpath_file}\n'
                    f'Application Libraries file: {self.application_libraries_file}\n')
        self.write_to_reportlog(report)

    def generate(self):
        self.environment_variable = self.environment_variable_entry.get()
        self.root_directory = self.root_directory_entry.get()
        self.classpath_file = self.classpath_file_entry.get()
        self.application_libraries_file = self.application_libraries_entry.get()

        if not os.path.exists(self.root_directory):
            messagebox.showerror("Error", "Root path " + self.root_directory + " doesn't exist")
            return
        
        output_log = self.get_file_path_in_current_directory('report.log')
        if os.path.isfile(output_log):
            os.remove(output_log)
        
        if self.classpath_file.strip() == "":
            self.reset_classpath()

        if self.application_libraries_file.strip() == "":
            self.reset_application_libraries()

        self.generate_global_libraries()

        messagebox.showinfo("Success", "Global Libraries generated successfully")

        self.config_data["environment_variable"] = self.environment_variable
        self.config_data["root_directory"] = self.root_directory
        self.config_data["classpath_file"] = self.classpath_file
        self.config_data["application_libraries_file"] = self.application_libraries_file

        self.save_config()
        self.generate_report()

    def cancel(self):
        self.destroy()


if __name__ == "__main__":
    app = EclipseToIntelliJ()
    app.mainloop()