# Author: Zachary Schmidt
# Collaborators: Jason Kim, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This files contains all the functions need to parse the Excel file
# containing the course category information

# Dependencies: copy, tkinter, xlrd, p

import xlrd
from copy import deepcopy
from tkinter import messagebox
from . import parsinghelp

# Parses an Excel file for categorical info about each course (is it 
# a math course, design, basic science, etc.) Also stores the color code
# provided in the Excel file for each course.
#
# Parameters:
#   filename (string): relative path to the file to be parsed for category info.
#       Can only be a .xls (not .xlsx file).
#   course_obj_dict (dict): Stores all course data:
#       key: Course Name (string): the Subject + " " + Catalog of a course
#       value: Course object. Stores all data about a course
# Returns:
#   course_obj_dict (dict): the category and color attributes should be
#       filled in
#   category_dict (dict):
#       Key: category (string): A category ("Basic Science", "Math", etc.)
#       Value: color (string): six char hex rrggbb color code for that category
def parseCategories(filename, course_obj_dict):
    try:
        category_dict = {}
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(0)

        for col in range(0, sheet.ncols):
            # Each column is one category
            cat_name = str(sheet.cell_value(0, col))  # first cell is category name
            if "." in str(sheet.cell_value(1, col)):
                # If rrggbb is all numbers, Excel likes to add a decimal point. Remove this
                dotindex = str(sheet.cell_value(1, col)).find(".")
                color = str(sheet.cell_value(1, col))[:dotindex]
            else:
                # It is formatted fine as it is
                color = str(sheet.cell_value(1, col))

            # store the category and color in a dict
            category_dict[cat_name] = color 

            # Create a new course object if an elective because elective info is not in course_obj_dict
            if cat_name.upper().strip() == "COMP" and "Complementary Elective" not in course_obj_dict:
                course_obj_dict["Complementary Elective"] = parsinghelp.Course(name = "Complementary Elective", 
                    course_description="A complementary elective of the student's choice. Please consult the calendar for more information.",
                    category = "Complementary Elective", color = color)
            if cat_name.upper().strip() == "PROG" and "Program/Technical Elective" not in course_obj_dict:
                course_obj_dict["Program/Technical Elective"] = parsinghelp.Course(name = "Program/Technical Elective", 
                    course_description="A program/technical elective of the student's choice. Please consult the calendar for more information.",
                    category = "Program/Technical Elective", color = color)
            if cat_name.upper().strip() == "ITS" and "ITS Elective" not in course_obj_dict:
                course_obj_dict["ITS Elective"] = parsinghelp.Course(name = "ITS Elective", 
                    course_description="An ITS elective of the student's choice. Please consult the calendar for more information.",
                    category = "ITS Elective", color = color)

            # Add category information to courses in that category
            course_obj_dict = addCategorytoCourses(course_obj_dict, sheet, col, cat_name, color)

       
    except FileNotFoundError:
        print("Excel course categories file not found, ensure it is present and the name is correct.")
        #GUI Error mssg
        messagebox.showerror('Python Error', "Excel course categories file not found, ensure it is present and the name is correct.")
    except xlrd.biffh.XLRDError:
        print("Error reading data from course categories Excel sheet. Ensure it is \
            formatted exactly as specified")
        #GUI Error mssg
        messagebox.showerror('python Error', "Error reading data from course categories Excel sheet. Ensure it is \
            formatted exactly as specified")

    return course_obj_dict, category_dict

# Function that adds the category information to courses of a specfic category
# Parameters:
#   - course_obj_dict: dict that maps the course name to a course object
#   - sheet: sheet handle to Excel sheet
#   - col: column number for respective category
#   - cat_name: name of respective category
#   - color: colour of respective category
def addCategorytoCourses(course_obj_dict, sheet, col, cat_name, color):
        for row in range(2, sheet.nrows):
                # Course names start at third row
                name = sheet.cell_value(row, col)
                if name == "":
                    continue
                name = name.upper().strip().replace("  ", " ")
                # guard to prevent key not found error
                if name in course_obj_dict: 
                    course_obj_dict[name].category = cat_name
                    course_obj_dict[name].color = color
        return course_obj_dict
