import os

import logging
#from logging import config
#config.fileConfig("../logging_config.py")
logger = logging.getLogger(__name__)

class FileUtil():
    project_root_path = ""

    def __init__(self, root=""):
        """
        A file utility class. The construction initializes project_root_path to the project's root directory, or sets it to the value
        of 'root'.
        """
        if root=="":
            self.project_root_path = os.path.dirname(os.path.abspath(__file__))
        else:
            self.project_root_path = root
        logger.info(f"Project root path set to: {self.project_root_path}")
    
    def find_file(self, filepath:str, backtrace:int = 6):
        """
        Attempts a search for a relative filepath, by conducting a backwards-folder search. This function, unlike find_win_abs_filepath,
        cannot be statically called, meaning find_file(...) must be called on an instantiated FileUtil instance.

        Parameters:
          - filepath: a relative filepath to find. Can be a single file (eg. data.json) or a file in a folder(s) eg. program_data/data/data.json
          - backtrace: the amount of levels to scan backwards
        
        Calling:
            from .FileUtil import FileUtil
            fu = new FileUtil()
            fu.find_file(FILEPATH)
          
        Returns the correct path to filepath, if it is found during the amount of 'backtraces' performed on the root filepath computed during init of this class
        by os.path.dirname(os.path.abspath(__file__)).

        A better alternative for finding a relative path to a file on windows is by using (FileUtil).find_win_abs_path(...)
        """
        def check_contains(folder_path, element_name):
            """
            Checks if 'filename' is in 'folder_path'.

            Parameters:
              - folder_path: the path to the folder where to search
              - element_name: either a filename or a folder name

            Return True if found or False if not found
            """
            folder_elements = os.listdir(folder_path)
            for folder_element in folder_elements:
                if folder_element == element_name:
                    return True
            return False
        
        # bugfix: sometimes when using os.path.join("folder1/folder2", "file1"), the result can be: folder1/folder2\file1
        if "\\" in filepath and "/" in filepath:
            filepath = filepath.replace("\\", "/")
            
        # first, see if is a single file or a file inside folder(s)
        folders = []
        file = ""
        if os.sep in filepath:
            folders = filepath.split(os.sep)[:-1] # folders are all but the last element
            file = filepath.split(os.sep)[-1] # file is the last in filepath
        elif "/" in filepath:
            folders = filepath.split("/")[:-1] # folders are all but the last element
            file = filepath.split("/")[-1] # file is the last in filepath
        else:
            file = filepath
        
        current_path = self.project_root_path
        if len(folders) == 0: # filepath is a single file
            for i in range(backtrace): # ascend 'backtrace' levels to the parent directory
                # we ascend a directory using os.path.dirname on a filepath
                if i != 0: # don't ascend up 1 directory on the first iteration
                    parent_path = os.path.dirname(current_path)
                    current_path = parent_path
                elif i == 0: # stay on the root for the first iteration
                    parent_path = current_path
                if check_contains(parent_path, file):
                    # file was found in parent_path
                    base_path = self.project_root_path
                    for j in range(i): # append i number of backtraces
                        base_path = os.path.join(base_path, "..")
                    return os.path.join(base_path, file) # return the correct path
        
        current_path = self.project_root_path # reset
        if len(folders) != 0: # filepath contains folders, primary search is for folder
            for i in range(backtrace):
                if i != 0:
                    parent_path = os.path.dirname(current_path)
                    current_path = parent_path
                elif i == 0:
                    parent_path = current_path
                if check_contains(parent_path, folders[0]):
                    # folder was found in parent path
                    base_path = self.project_root_path
                    for j in range(i): # append i number of backtraces
                        base_path = os.path.join(base_path, "..")
                    # append the folders
                    for folder in folders:
                        if check_contains(base_path, folder):
                            base_path = os.path.join(base_path, folder)
                        else:
                            logger.info(f"ERROR during file search. Base path {base_path} doesn't contain folder {folder}")
                    # finally, append the file
                    return os.path.join(base_path, file)
    
    @classmethod
    def find_win_abs_filepath(cls, relative_filepath: str):
        """
        Finds the absolute filepath to specified 'relative_filepath' using os.getcwd(). Note, that the function does not include
        the "self" parameter, therefore it can be statically called using FileUtil.find_win_abs_filepath(...) without instantiating
        a FilePath instance.

        Parameters:
          - (str) relative_filepath: a relative filepath from the root of the project's directory to the file
        
        Calling:
            from .FileUtil import FileUtil
            FileUtil.find_win_abs_filepath(FILEPATH)
        
        Returns:
          - an absolute filepath to the specified relative filepath: os.getcwd + relative filepath
        """
        if "/" in relative_filepath:
            relative_filepath = relative_filepath.replace("/", os.sep)
        
        return os.path.join(os.getcwd(), relative_filepath)
    
    @classmethod
    def get_workspace_dir(cls):
        """
        Returns the workspace-specific directory using os.getcwd().
        """
        return os.getcwd()
    
    def write_to_txt_file(self, list:list, filepath = "", filename=""):
        """
        Writes the input list, line by line to the specified filepath. If no filepath is specified,
        file is written to self.project_root_path/filename.txt. If filename is also not specified, then
        the lines are written to self.project_root_path/text.txt
        """
        # TODO: implement

    @classmethod
    def write_to_txt_file(cls, list:list, filepath: str):
        """
        Writes the input list, line by line, to the specified filepath.
        """
        filepath = cls.find_win_abs_filepath(filepath)
        with open(filepath, "w") as f:
            for element in list:
                line = element
                if "\n" not in line:
                    line = f"{line}\n"
                f.write(line)
    
    @classmethod
    def is_file_empty(cls, filepath:str):
        """
        Checks if 'filepath' is an empty file. Returns True if the file is empty.
        """
        return True if os.path.getsize(filepath) == 0 else False