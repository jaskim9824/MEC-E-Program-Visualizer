# Author: Zachary Schmidt
# Collaborators: Jason Kim, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This file contains the functions neccesary to parse the Excel file
# containing the sequncing information

# Dependencies: copy, tkinter, xlrd

from copy import deepcopy
from tkinter import messagebox
import xlrd


# Parses an Excel file with program sequencing information (when courses are taken)
# and returns a dictionary storing the program plan name as key (Traditional, Co-op plan 1, etc.)
# and a dict as value. This inner dict has the term name (Term 1, Term 2, etc.) as key
# and a list of Course objects as value.
#
# Parameters:
#   course_obj_dict (dictionary): dict with course name for key and 
#   Course class as value. Course class described in parsing.py
#   filename (string): Name of the Excel file to be parsed for sequencing
#   info. Format described in README. Can only be a .xls file (NOT .xlsx)
#
# Returns:
#   course_seq (dictionary): Key is plan name, value is another dict with 
#   term name as the key and a list of the Course objects taken in that term as value.
def parseSeq(filename, course_obj_dict):
    try:
        book = xlrd.open_workbook(filename)
        numsheets = book.nsheets
        course_seq = {}

        for i in range(0, numsheets):
            # Each sheet stores a plan (traditional, co-op plan 1, etc.)
            plan_dict = {}
            sheet = book.sheet_by_index(i)
            if i == 0:
                dept_name = sheet.cell_value(0, 0)
                col = 1
            else:
                col = 0
            while col < sheet.ncols:
                # Each column represents a term
                term_name = sheet.cell_value(0, col)  # first entry in col must be the term name
                term_list = []  # stores Course objects in a list for that term
                for row in range(1, sheet.nrows):
                    name = str(sheet.cell_value(row, col))
                    name = name.upper()  # course name must be uppercase
                    # Remove unnecessary white space
                    name = name.strip()
                    name = name.replace("  ", " ")
                    if name == "":
                        # Cell in Excel is empty, skip over this cell
                        continue
                    course_group = ""
                    if name[-1] == "A":
                        course_group = "A"
                        name = name[:-1]
                    if name[-1] == "B":
                        course_group = "B"
                        name = name[:-1]

                    if name == "PROG":
                        # Create Course obj with only name and course_description attribute
                        curr_course = deepcopy(course_obj_dict["Program/Technical Elective"])
                        if course_group == "A":
                            curr_course.course_group = "A"
                        elif course_group == "B":
                            curr_course.course_group = "B"
                        term_list.append(curr_course)
                        continue
                    if name == "COMP":
                        curr_course = deepcopy(course_obj_dict["Complementary Elective"])
                        if course_group == "A":
                            curr_course.course_group = "A"
                        elif course_group == "B":
                            curr_course.course_group = "B"
                        term_list.append(curr_course)
                        continue
                    if name == "ITS":
                        curr_course = deepcopy(course_obj_dict["ITS Elective"])
                        if course_group == "A":
                            curr_course.course_group = "A"
                        elif course_group == "B":
                            curr_course.course_group = "B"
                        term_list.append(curr_course)
                        continue

                    if "OR" in name:
                        namelist = name.split("OR")
                        for orname in namelist:
                            orname = orname.strip()
                            assert orname in course_obj_dict, ("The course in the Sequencing.xls file called " + 
                                name + " on sheet " + sheet.name + " on row " + str(row) + " and column " + str(col) +
                                " is not present in the Excel file with the course information.")
                            orcourse = deepcopy(course_obj_dict[orname])
                            orcourse.calendar_print = "or"
                            if course_group == "A":
                                orcourse.course_group = "A"
                            elif course_group == "B":
                                orcourse.course_group = "B"
                            term_list.append(orcourse)
                        plan_dict[term_name] = term_list
                        row += 1
                        continue

                    assert name in course_obj_dict, ("The course in the Sequencing.xls file called " + 
                        name + " on sheet " + sheet.name + " on row " + str(row) + " and column " + str(col) +
                        " is not present in the Excel file with the course information.")

                    # deepcopy since sequencing leads to prereqs and coreqs not being the same between different plans
                    curr_course = deepcopy(course_obj_dict[name])
                    if course_group == "A":
                        curr_course.course_group = "A"
                    elif course_group == "B":
                        curr_course.course_group = "B"
                    term_list.append(curr_course)  # store each course in a list
                plan_dict[term_name] = term_list  # store each list in a dict (key is term name)
                col += 1
            course_seq[sheet.name] = plan_dict  # store each term dict in a plan dict (key is plan name (traditional, etc.))

        # Make sure that co-reqs are only for courses in the same term
        # Had to do this after pulling from Sequencing.xls
        # course_seq = checkReqs(course_seq)  Not used, keep everything exactly like Calendar

    except FileNotFoundError:
        print("Excel sequencing file not found, ensure it is present and the name is correct.")
        #GUI Error mssg
        messagebox.showerror('Python Error', "Excel sequencing file not found, ensure it is present and the name is correct.")
    except xlrd.biffh.XLRDError:
        print("Error reading data from sequencing Excel sheet. Ensure it is \
            formatted exactly as specified")
        #GUI Error mssg
        messagebox.showerror('python Error', "Error reading data from sequencing Excel sheet. Ensure it is \
            formatted exactly as specified")

    return course_seq, dept_name

# Checks that all coreqs for a course are taken in the same term,
# if not, the coreq is changed to become a prereq. Similarly,
# if a coreq is actually taken before a course in a certain plan,
# that coreq is changed to a prereq for that course.
#
# Parameters:
#   course_seq (dict): Stores course data in proper sequence:
#       key: Plan Name (string): name of the sheet from "Sequencing.xls"
#       ("Traditional", "Co-op Plan 1", etc.)
#       value: dict with key as term name ("Term 1", "Term 2", etc.)
#
# Returns:
#   course_seq (dict): Stores course data in proper sequence:
#       key: Plan Name (string): name of the sheet from "Sequencing.xls"
#       ("Traditional", "Co-op Plan 1", etc.)
#       value: dict with key as term name ("Term 1", "Term 2", etc.)
#       and value as a list of Course objects to be taken in that term.
#       The coreq and prereq attributes may or may not have been modified.
def checkReqs(course_seq):
    # We have to check the sequencing for each plan as courses are taken
    # at different times in different plans
    for plan in course_seq:
        # stores all of the names of the courses to be taken in this plan
        all_names = extractCoursesFromPlan(course_seq, plan)
        
        planDict = course_seq[plan]
        for term in planDict:
            # stores all of the names of the courses to be taken in this term
            term_course_names = extractCourseFromTerm(planDict, term)
       
            for course in planDict[term]:
                # FIXME: fix for ENGG 160 coreq calendar description
                if course.name == "ENGG 160":
                    continue
                # Checking coreqs
                for coreq in course.coreqs:
                    # For each coreq for a certain course, if there are multiple options
                    # (MATH 100 or MATH 114 or...) then only keep those that are displayed
                    # in this plan. eg: Coreqs: MATH 100 or MATH 114, if only MATH 100 is 
                    # available in this plan, discard MATH 114 and keep MATH 100.
                    coreqlist = coreq.split(" or ")

                    i = 0
                    while i < len(coreqlist):
                        if coreqlist[i] not in all_names:
                            # If the coreq is not available in this plan, delete it
                            del coreqlist[i]
                            continue
                        i += 1

                    if coreqlist != []:
                        coreq_count = 0
                        while coreq_count < len(coreqlist):
                            if coreqlist[coreq_count] not in term_course_names:
                                # The coreq course in not taken in the same term,
                                # it is really a prereq
                                course.prereqs.append(coreqlist[coreq_count])
                                if coreq in course.coreqs:
                                    del course.coreqs[course.coreqs.index(coreq)]
                            coreq_count += 1

                # Analagous situation but for prereqs (not coreqs)
                for prereq in course.prereqs:
                    # For each prereq for a certain course, if there are multiple options
                    # (MATH 100 or MATH 114 or...) then only keep those that are displayed
                    # in this plan. eg: Prereqs: MATH 100 or MATH 114, if only MATH 100 is 
                    # available in this plan, discard MATH 114 and keep MATH 100.
                    prereqlist = prereq.split(" or ")
                    i = 0
                    while i < len(prereqlist):
                        # If the prereq is not available in this plan, delete it
                        if prereqlist[i] not in all_names:
                            del prereqlist[i]
                            continue
                        i += 1

                    if prereqlist != []:
                        prereq_count = 0
                        while prereq_count < len(prereqlist):
                            if prereqlist[prereq_count] in term_course_names:
                                # The prereq course is taken in the same term,
                                # it is really a coreq
                                course.coreqs.append(prereqlist[prereq_count])
                                if prereq in course.prereqs:
                                    del course.prereqs[course.prereqs.index(prereq)]
                            prereq_count += 1
 
    return course_seq

def extractCoursesFromPlan(course_seq, plan):
    all_names = []
    for term in course_seq[plan]:
        for course in course_seq[plan][term]:
            course_name = course.name.replace(" ", "").replace("or", " or ")
            all_names.append(course_name)
    return all_names

def extractCourseFromTerm(planDict, term):
    term_course_names = []
    for course in planDict[term]:
        course_name = course.name.replace(" ", "").replace("or", " or ")
        term_course_names.append(course_name)
    return term_course_names



