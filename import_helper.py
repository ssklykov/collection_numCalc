#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Attempt to create the  unified class for importing dependecies by compiling previously developed functionality
Reason behind - to make something functional to search / import modules if the containing it directory tree isn't
included in any project

@author: ssklykov
"""
# %% Imports
import os
# import sys


# %% Holding attributes for a folder in class (maybe, redundant)
class folder():
    absolute_path = ""
    relative_path = ""
    subfolders = []
    files = []
    size = 0
    default_excluded_dirs = []
    # For testing capabilities below is narrowing of output
    default_excluded_folders = []

    def __init__(self, absolute_path: str, relative_path: str,
                 default_excluded_dirs: list = [".git", ".gitignore", "__pycache__"]):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.default_excluded_dirs = default_excluded_dirs
        self.subfolders = projectImport.getDirList(absolute_path, default_excluded_dirs)
        entries = os.listdir(absolute_path)
        self.files = []
        for entry in entries:
            if os.path.isfile(os.path.join(absolute_path, entry)):
                self.files.append(entry)

    def __str__(self):
        """For debugging by printing all info about folder after calling print(instance_this_class)"""
        overall_description = "Extended by OOP folder on the path: \n"
        overall_description += (self.absolute_path + " \n")
        overall_description += "Contains following subfolders: \n"
        overall_description += (str(self.subfolders) + "\n")
        overall_description += "And also contains following files: \n"
        overall_description += (str(self.files) + "\n")
        return overall_description


# %% Class implementation
class projectImport():
    """Class for holding all support methods for importing / searching."""
    projectTree = {}
    anchorFolder = ""
    containingFolder = ""
    projectPath = ""
    osSpecificSeparator = ""
    listOFAllPathsToDirs = []
    listOfFilesNames = []
    listOfDirs = []
    default_excluded_dirs = []

    def __init__(self, anchorFolder: str = ".git", default_excluded_dirs: list = [".git", ".gitignore", "__pycache__"]):
        """
        Initialization along attempting to collect project structure.

        Parameters
        ----------
        anchorFolder : str, optional
            The anchor folder should be in the project main directory tree. The default is ".git" that is presented
            for version controlled projects in Git.
        Returns
        -------
        Sample of class, actually.

        """
        self.containingFolder = os.getcwd()
        self.osSpecificSeparator = os.sep
        iteration_depth = 5  # Iteration depth for operation of going in hierarchy of folders up
        iteration = 1
        # Searching and collecting absolute path to anchor folder - that on the same level of the whole project
        while (anchorFolder not in os.listdir(os.curdir)) and (iteration <= iteration_depth):
            os.chdir("..")
            iteration += 1
        if (iteration == 5) and (anchorFolder not in os.listdir(os.curdir)):
            print("Anchor folder didn't found")
            self.anchorFolder = None
            self.projectPath = self.containingFolder
        else:
            self.projectPath = os.path.abspath(os.curdir)
            self.anchorFolder = anchorFolder
            folderTree = os.listdir(self.projectPath)  # Get all files and folders in the expected project tree
            if len(folderTree) > 0:  # If project tree is non-empty
                folderTree = projectImport.deleteGitFolders(folderTree)
            else:
                self.projectTree[self.projectPath] = "Empty"
            # Again, checking that it's not an empty git project
            if len(folderTree) > 0:
                self.projectTree[self.projectPath] = folderTree
            else:
                self.projectTree[self.projectPath] = "Empty"

    # %% Attempts to make a project structure with folders as nodes of graphs
    def buildProjectDirGraph(self):
        # Second attempt to write recursive iterator building the project folder graph
        rootPath = self.projectPath
        walkDone = False
        # First iteration not in the loop (for making clear for myself mostly):
        node = {}
        (root, tail) = os.path.split(rootPath)
        node[tail] = projectImport.getDirList(rootPath, self.default_excluded_dirs)  # Representation of a node - folder
        j = 0
        rootName = tail  # For keeping the name of a root directory
        projectFolder = folder(rootPath, "/")
        # print(projectFolder)
        self.listOfDirs.append(projectFolder)
        dirs_to_visit = projectImport.convert_subfolds_to_abs_paths(rootPath, projectFolder.subfolders)
        # print("dirs_to_visit: ", dirs_to_visit)

        # j - for only preventing any unexpected infinite loops
        while (not walkDone) and (j < 100000):
            if len(dirs_to_visit) > 0:
                current_path = dirs_to_visit[0]
                rel_path = projectImport.make_rel_path(rootName, current_path)
                new_dir = folder(current_path, rel_path)
                self.listOfDirs.append(new_dir)
                dirs_to_visit.pop(0)  # delete visited folder
                if len(new_dir.subfolders) > 0:
                    new_dirs_to_visit = projectImport.convert_subfolds_to_abs_paths(current_path, new_dir.subfolders)
                    dirs_to_visit += new_dirs_to_visit
                # print(new_dir)
            else:
                walkDone = True
            j += 1

    @staticmethod
    def convert_subfolds_to_abs_paths(root: str, subfolders: list) -> list:
        converted = []
        for subfolder in subfolders:
            updated_path = root + "/" + subfolder
            converted.append(updated_path)
        return converted

    @staticmethod
    def make_abs_path(rootPath, path_in_project_struct: list) -> str:
        absolute_path = rootPath
        for folder in path_in_project_struct:
            new_p = "/" + folder
            absolute_path += new_p
        return absolute_path

    @staticmethod
    def split_relative_path(relative_path: str) -> list:
        all_nodes = relative_path.split("/")
        return all_nodes

    @staticmethod
    def make_rel_path(rootPath: str, current_path: str):
        all_folders = os.path.split("/")
        for i in range(len(all_folders)):
            if rootPath == all_folders[i]:
                break
        root = ""
        for j in range(i+1, len(all_folders)):
            root += "/" + all_folders[j]
        return root

    # %% Useful methods - used somewhere else in this script

    @staticmethod
    def getDirList(rootPath: str, excludingFolders: list) -> list:
        """
        Returns of list of dirs down from specified path (specified path should point to some folder).

        Parameters
        ----------
        rootPath : str
            Path to the root directory
        excludingFolders : list, optional
            List with names of folders that must be excluded from returning list.
            The default is [".git, .gitignore"].

        Returns
        -------
        list
            List with folder names that the root directory contains.

        """
        if os.path.exists(rootPath):
            listOfDirs = os.listdir(rootPath)
            i = 0
            while i < len(listOfDirs):
                pathToObj = os.path.join(rootPath, listOfDirs[i])
                if (not os.path.isdir(pathToObj)) or (listOfDirs[i] in excludingFolders):
                    listOfDirs.pop(i)
                else:
                    i += 1
            return listOfDirs
        else:
            return []

    @staticmethod
    def includeFileToSysPath(absPathToFolder: str):
        import sys
        # print("sys.path before: ", sys.path)
        if (sys.path.count(absPathToFolder) == 0):
            sys.path.append(absPathToFolder)
        elif (sys.path.count(absPathToFolder) > 1):
            for i in (2, sys.path.count(absPathToFolder)):
                sys.path.remove(absPathToFolder)
        # print("sys.path after: ", sys.path)

    @staticmethod
    def deleteGitFolders(folderTree: list) -> list:
        """Deleting specific for git controlled projects folders .git and .gitignore from a project tree"""
        i = 0
        while i < len(folderTree):
            if (folderTree[i] == '.git') or (folderTree[i] == ".gitignore"):
                folderTree.pop(i)
                # print("Deleted folder", delF)
            else:
                i += 1
        return folderTree

    def printAllSelfValues(self):
        """
        For debugging / testing - enabling it for get output
        """
        print("*********************************")
        # print("The folder containing this script:", self.containingFolder)
        # print("specific folder separator:", self.osSpecificSeparator)
        # print("Expected project tree containing the anchor:", self.projectPath)
        print("Collected paths to folders: ", self.listOFAllPathsToDirs)


# %% Testing some capabilities
if __name__ == "__main__":
    demo_instance = projectImport()
    # demo_instance.recursiveBuildDirGraph()
    # demo_instance.makeDirectoryGraph()
    # demo_instance.printAllSelfValues()
    demo_instance.buildProjectDirGraph()
    # included = demo_instance.includeFileToSearchPath("LICENSE")
    # demo_instance2 = projectImport("Some non-exist folder")
    # demo_instance2.printAllSelfValues()

# For testing capabilities - some parameters
    # default_excluded_folders = [".git", ".gitignore", "Matricies_Manipulation", "Sorting", "Plotting",
    #                             "Experimental", "LinearSystems", "Interpolation", "FunctionRoots", "__pycache__",
    #                             "MonteCarlo"]
