# Author: Zachary Schmidt
# Collaborators: Jason Kim, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This file contains all the functions needed to parse the Excel file
# containing the course information 

# Dependencies: copy, xlrd, parsinghelp

import xlrd
from copy import deepcopy
from . import parsinghelp

# Parses a .xls (NOT .xlsx) file located at the
# relative path *filename* and stores all relevant course information
# in a dict
#
# Parameters:
#   filename (string): path to the .xls file with course information (relative to the calling script)
# Returns:
#   course_obj_dict (dict): Stores all course data:
#       key: Course Name (string): the Subject + " " + Catalog of a course
#       value: Course object. Stores all data about a course
def parseCourses(filename):
    try:
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(0)  # course info must be on the first sheet
        course_obj_dict = {}
        for row in range(1, sheet.nrows):
            # Each row stores info about one course, first row is headers
            faculty = sheet.cell_value(row, 0)
            department = sheet.cell_value(row, 1)
            course_id = sheet.cell_value(row, 2)
            subject = sheet.cell_value(row , 3)
            catalog = sheet.cell_value(row, 4)
            long_title = sheet.cell_value(row, 5)
            eff_date = sheet.cell_value(row, 6)
            status = sheet.cell_value(row, 7)
            calendar_print = sheet.cell_value(row, 8)
            prog_units = sheet.cell_value(row, 9)
            engg_units = sheet.cell_value(row, 10)
            calc_fee_index = sheet.cell_value(row, 11)
            actual_fee_index = sheet.cell_value(row, 12)
            duration = sheet.cell_value(row, 13)
            alpha_hours = sheet.cell_value(row, 14)
            course_description = sheet.cell_value(row, 15)

            # Formatting course name
            course_name = str(subject) + " " + str(catalog)

            # Remove unnecessary whitespace
            course_name = course_name.strip().replace("  ", " ")

            main_category = ""
            sub_categories = []
            color = ""
            course_group = ""
            prereqs = []
            coreqs = []
            elective_group = ""
            accredUnits = {"Math":0, "Natural Sciences":0, "Math and Natural Sciences":0,
            "Complimentary Studies":0, "Engineering Science":0, "Engineering Design":0, 
            "Engineering Science and Engineering Design":0, "Other":0}

            # Adding deepcopy of course to dict
            course_obj_dict[course_name] = deepcopy(parsinghelp.Course(course_name, faculty,
            department, course_id, subject, catalog, long_title,
            eff_date, status, calendar_print, prog_units, engg_units,
            calc_fee_index, actual_fee_index, duration, alpha_hours,
            course_description, main_category, sub_categories, color,
            course_group, prereqs, coreqs, elective_group, accredUnits))

        # Retrieving dependencies (pre/coreqs) for courses
        course_obj_dict = pullDependencies(course_obj_dict)

        return course_obj_dict

    except FileNotFoundError:
        raise FileNotFoundError("Excel course information file not found, ensure it is present and the name is correct.")
    except xlrd.biffh.XLRDError:
        raise xlrd.biffh.XLRDError("Error reading data from Course information Excel sheet. Ensure it is formatted exactly as specified")

# Parses the accredFileName file for information on accreditation
# units satisfied by the courses in courseObjDict.
# Parameters:
#   courseObjDict (dict): dict with course name for key and 
#   Course object as value
#   accredFileName (string): name of the .xls file containing 
#   accreditation info
#   deptName (string): name of the department, should match the header
#   on one of the sheets in the accreditation info Excel file
def parseAccred(courseObjDict, accredFileName, deptName):
    try:
        book = xlrd.open_workbook(accredFileName)

        # open each sheet and check if header matches deptName
        sheet = None
        for i in range(0, book.nsheets):
            if book.sheet_by_index(i).cell_value(0, 1) == deptName:
                sheet = book.sheet_by_index(i)
        
        # if no matching department name found, display error message and continue execution
        if sheet is None:
            print("Department name: " + deptName + " does not match any sheet in the accreditation file")
            print("No accreditation unit information will be available on the generated webpage")
            return

        for row in range(4, sheet.nrows):
            if sheet.cell_value(row, 1) in courseObjDict:  # see if the Excel entry matches a course name
                # if there is a match, update the accredUnits field with corresponding values
                courseName = sheet.cell_value(row, 1)
                courseObjDict[courseName].accredUnits["Math"] = round(sheet.cell_value(row, 8), 1)
                courseObjDict[courseName].accredUnits["Natural Sciences"] = round(sheet.cell_value(row, 9), 1)
                courseObjDict[courseName].accredUnits["Math and Natural Sciences"] = round(sheet.cell_value(row, 10), 1)
                courseObjDict[courseName].accredUnits["Complimentary Studies"] = round(sheet.cell_value(row, 11), 1)
                courseObjDict[courseName].accredUnits["Engineering Science"] = round(sheet.cell_value(row, 12), 1)
                courseObjDict[courseName].accredUnits["Engineering Design"] = round(sheet.cell_value(row, 13), 1)
                courseObjDict[courseName].accredUnits["Engineering Science and Engineering Design"] = round(sheet.cell_value(row, 14), 1)
                courseObjDict[courseName].accredUnits["Other"] = round(sheet.cell_value(row, 15), 1)

    except FileNotFoundError:
        raise FileNotFoundError("Excel accreditation information file not found, ensure it is present and the name is correct")
    except xlrd.biffh.XLRDError:
        raise xlrd.biffh.XLRDError("Error reading data from accreditation information Excel sheet. Ensure it is formatted exactly as specified")

# Pulls all course dependencies (prerequisites, corequisites, and
# requisites) for each course in course_obj_dict. Dependencies stored
# in lists as attributes of the Course object.
#
# Parameters:
#   course_obj_dict (dict): Stores all course data:
#       key: Course Name (string): the Subject + " " + Catalog of a course
#       value: Course object. Stores all data about a course
# Returns:
#   course_obj_dict (dict): the prereqs, coreqs, and reqs attributes should
#       be filled in
def pullDependencies(course_obj_dict):
    for course in course_obj_dict:
        prereqslist = pullPreReqs(course_obj_dict[course].course_description)
        for i in range(0, len(prereqslist)):
            # stripping whitespace
            prereqslist[i] = prereqslist[i].replace(" ", "").replace("or", " or ")
        course_obj_dict[course].prereqs = prereqslist

        coreqslist = pullCoReqs(course_obj_dict[course].course_description)
        for i in range(0, len(coreqslist)):
            # stripping whitespace
            coreqslist[i] = coreqslist[i].replace(" ", "").replace("or", " or ")
        course_obj_dict[course].coreqs = coreqslist

    return course_obj_dict

# Pulls the prerequisites from the course description.
#
# Parameters:
#   description (string): The complete course description taken from the Calendar
# Returns:
#   prereqs (list of strings): A list of the prerequisites. Elements
#   can be in two forms: 1) The name of a single course. eg: "MATH 100"
#   2) Several courses, each separated by the word " or ". This indicates that only one of
#   these courses is required as a prerequisite. eg: "MEC E 250 or MATH 102 or CH E 441"
def pullPreReqs(description):
    description.replace("-requisite", "requisite")
    # Split into cases, plural and not plural. Just adjusts the substring value (14 or 15)
    singlestart = description.find("Prerequisite: ")
    if singlestart == -1:
        singlestart = description.find("prerequisite: ")

    multstart = description.find("Prerequisites: ")
    if multstart == -1:
        multstart = description.find("prerequisites: ")

    missingcolstart = description.find("Prerequisite ")
    if missingcolstart == -1:
        missingcolstart = description.find("prerequisite ")

    if singlestart != -1:
        # Prerequisite(s) given from after the colon up to the very next period
        singlestart += 14
        singleend = description.find(".", singlestart)
        prestr = description[singlestart:singleend]     
    elif multstart != -1:
        # Prerequisite(s) given from after the colon up to the very next period
        multstart += 15
        multend = description.find(".", multstart)
        prestr = description[multstart:multend]
    elif missingcolstart != -1:
        # Prerequisite(s) given from after space up to the very next period
        missingcolstart += 13
        missingcolend = description.find(".", missingcolstart)
        prestr = description[missingcolstart:missingcolend]
    else:
        return []

    # Process the string to split it into a list with each item being the name
    # of a prerequisite course
    prereqs = process(prestr)
    
    return prereqs

# Pulls the corequisites from the course description.
#
# Parameters:
#   description (string): The complete course description taken from the Calendar
# Returns:
#   coreqs (list of strings): A list of the corequisites. Elements
#   can be in two forms. 1) The name of a single course. eg: "MATH 100"
#   2) Several courses, each separated by the word "or". This denotes that only one of
#   these courses is required as a corequisite. eg: "MEC E 250 or MATH 102 or CH E 441"
def pullCoReqs(description):
    description.replace("-requisite", "requisite")
    # Split into cases, plural and not plural. Just adjusts the substring value (14 or 15)
    singlestart = description.find("Corequisite: ")
    if singlestart == -1:
        singlestart = description.find("corequisite: ")

    multstart = description.find("Corequisites: ")
    if multstart == -1:
        multstart = description.find("corequisites: ")

    missingcolstart = description.find("Corequisite ")
    if missingcolstart == -1:
        missingcolstart = description.find("corequisite ")

    if singlestart != -1:
        # Corequisite(s) given from after the colon up to the very next period
        singlestart += 13
        singleend = description.find(".", singlestart)
        prestr = description[singlestart:singleend]     
    elif multstart != -1:
        # Corequisite(s) given from after the colon up to the very next period
        multstart += 14
        multend = description.find(".", multstart)
        prestr = description[multstart:multend]
    elif missingcolstart != -1:
        # Corequisite(s) given from after space up to the very next period
        missingcolstart += 12
        missingcolend = description.find(".", missingcolstart)
        prestr = description[missingcolstart:missingcolend]
    else:
        return []

    # Process the string to split it into a list with each item being the name
    # of a corequisite course
    coreqs = process(prestr)
    
    return coreqs

# Pulls the pre-requisites from a course description. Returns the 
# pre-requisites as a list of strings, each element being the name of
# a pre-requisite course.
#
# Parameters:
#   prestr (string): The part of a course description from "Prerequisites: " (or variant)
#   until the next period. eg: "Prerequisites: **One of CH E 441, MEC E 250, or MATH 100.**" 
#   Everything between the ** should be passed.
# Returns: 
#   reqlist (list of strings): A list of the pre-requisites of a course. Elements
#   can be in two forms: 1) The name of a single course. eg: "MATH 100"
#   2) Several courses, each separated by the word "or". This denotes that only one of
#   these courses is required as a prerequisite. eg: "MEC E 250 or MATH 102 or CH E 441"
def process(prestr):
    prestr = prestr.strip()
    prestr = prestr.replace("\n", " ")
    # Add a comma after the end of each course name
    prestr = prestr.replace("0 ", "0, ")
    prestr = prestr.replace("1 ", "1, ")
    prestr = prestr.replace("2 ", "2, ")
    prestr = prestr.replace("3 ", "3, ")
    prestr = prestr.replace("4 ", "4, ")
    prestr = prestr.replace("5 ", "5, ")
    prestr = prestr.replace("6 ", "6, ")
    prestr = prestr.replace("7 ", "7, ")
    prestr = prestr.replace("8 ", "8, ")
    prestr = prestr.replace("9 ", "9, ")
    prestr = prestr.replace(" and", ",")
    prestr = prestr.replace("  ", " ")

    # Create a list, splitting at each course
    reqlist = prestr.split(", ")

    if reqlist is None:
        # If no prerequisites, return empty list
        return []

    reqlist = preprocess(reqlist)  # Helps format text by handling cases

    i = 0

    while i < len(reqlist):
        # Iterate through every element in reqlist. Changes are made
        # directly on reqlist
        reqlist[i] = reqlist[i].strip()

        if "-" in reqlist[i]:
            del reqlist[i]
            continue

        # Count the number of numbers (should be 3 if it's a course)
        numcounter = parsinghelp.countNums(reqlist[i])

        if reqlist[i][0:5] == "both " or reqlist[i][0:5] == "Both ":
            # Two courses are required, remove both and pull the department name if required
            reqlist[i] = reqlist[i].replace("both ","")
            reqlist[i] = reqlist[i].replace("Both ","")
            numcounter = parsinghelp.countNums(reqlist[i + 1])
            if numcounter == 3 and len(reqlist[i + 1]) == 3:
                # Only a course number is present, must pull the department name
                dept = parsinghelp.pullDept(reqlist, i)
                assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

                reqlist[i + 1] = dept + " " + reqlist[i + 1]

        if (reqlist[i][0:7] == "One of ") or (reqlist[i][0:7] == "one of ") or (reqlist[i][0:7] == "Either ") or (reqlist[i][0:7] == "either "):
            # Same logic for "one of" and "either"
            if ((reqlist[i][0:6] == "Either") or (reqlist[i][0:6] == "either")) and (reqlist[i + 1][0:11] == "or one of "):
                # "or one of " is redundant
                # Remove the "or one of " and we can apply the same steps
                reqlist[i + 1] = reqlist[i + 1].replace("or one of ", "")

            # Only one of the upcoming courses is required
            reqlist[i] = reqlist[i].replace("One of ", "").replace("one of ", "").replace("Either ", "").replace("either ", "")

            j = i + 1  # i is where clause starts, j will increment until the clause is finished

            if j < len(reqlist):
                while ("or" not in reqlist[j]) and ("Or" not in reqlist[j]):
                    # There are still more courses that could be chosen (clause not done), 
                    # combine the previous and current elements, continue until we see the 
                    # word "or" or we reach the end of the reqlist

                    # Count the number of numbers in the next element
                    numcounter = parsinghelp.countNums(reqlist[j])

                    if numcounter == 3 and len(reqlist[j]) == 3:
                        # Only the course number is present, we need to pull
                        # the department from the previous element
                        # eg: [MATH 100, 102] should become [MATH 100, MATH 102]
                        dept = parsinghelp.pullDept(reqlist, j - 1)
                        assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

                        reqlist[j] = dept + " " + reqlist[j]  # add the department name
                    reqlist[i] = reqlist[i] + " or " + reqlist[j]  # combine previous and current elements
                    del reqlist[j]  # remove the current element from the list
                    if j >= len(reqlist):
                        break

                if j < len(reqlist):
                    if ("or" in reqlist[j]) or ("Or" in reqlist[j]):
                        # This is the last course that could be chosen, combine as before
                        # but don't add "or" (already present)

                        # Count the number of numbers in the next element
                        numcounter = parsinghelp.countNums(reqlist[j])

                        if numcounter == 3 and len(reqlist[j]) == 6:
                            # only "or" and a number is present eg: "or 451" (3 numbers, 6 chars)
                            # we need to pull the department from the previous element
                            dept = parsinghelp.pullDept(reqlist, j - 1)
                            assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

                            reqlist[j] = "or " + dept + reqlist[j][2:]  # move the position of "or"

                        if reqlist[j][0:8] == "or both ":
                            # FIXME: this is tough to deal with, either one set of courses can be chosen
                            # or both of these next courses can be chosen
                            # Right now, just combining everything into one list entry
                            if len(reqlist[j]) == 11:
                                # Only course number is present in current entry, need to pull department name from previous
                                dept = parsinghelp.pullDept(reqlist, j - 1)
                                assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

                                reqlist[j] = "or both " + dept + reqlist[j][7:]  # move the position of "or both"

                            numcounter = parsinghelp.countNums(reqlist[j + 1])
                            if numcounter == 3 and len(reqlist[j + 1]) == 3:
                                # Only course number is present in the next entry, need to pull the department name from current
                                dept = parsinghelp.pullDept(reqlist, j)
                                assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

                                # Re-arranging words
                                reqlist[j + 1] = "and " + dept[8:] + " " + reqlist[j + 1]
                                reqlist[j] = reqlist[j] + " " + reqlist[j + 1]  # combine current and next
                                del reqlist[j + 1]

                        reqlist[i] = reqlist[i] + " " + reqlist[j]  # combine current and previous
                        del reqlist[j]
                        if j >= len(reqlist):
                            break
            i += 1

        elif (reqlist[i][0:2] == "or" or reqlist[i][0:2] == "Or") and len(reqlist[i]) == 6:
            # The element is just "or" followed by a course number. eg: "or 451" 
            # The department is not present.
            # We need to pull the department from the previous element.
            dept = parsinghelp.pullDept(reqlist, i - 1)
            assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

            reqlist[i] = "or " + dept + reqlist[i][2:]  # move the position of "or"
            reqlist[i - 1] = reqlist[i - 1] + " " + reqlist[i]  # combine previous and current elements
            del reqlist[i]  # remove current element

        elif (reqlist[i][0:2] == "or" or reqlist[i][0:2] == "Or") and len(reqlist[i]) > 6:
            # The element is "or" followed by the course name with the department name present
            # eg: "or MATH 100"
            # Just combine the current and previous elements
            reqlist[i - 1] = reqlist[i - 1] + " " + reqlist[i]  # combine current and previous elements
            del reqlist[i]  # delete current element

        elif numcounter == 3 and len(reqlist[i]) == 3:
            # Only a course number is present. eg: "102"
            # All we do is pull the department from the previous element.
            dept = parsinghelp.pullDept(reqlist, i - 1)
            assert dept != -1, "Error pulling department name from previous list item, check pullDept()"

            reqlist[i] = dept + " " + reqlist[i]  # just add the department name to current item
            i += 1
            
        else:
            # No processing is required. Usually, this means reqlist[i] is a pre/co-req
            # with the department name present and is not one option among other courses.
            # eg: reqlist = [MATH 102]  no processing is required
            i += 1
    
    return reqlist

# Preprocesses a list (of strings) of the pre-requisites for one course.
# Removes all brackets and commas, replaces slash with " or ". If the list item is not a course
# (some text such as: "consent of the department required.") it is removed.
# Any text after a semicolon is removed. Any item that is longer than 16 chars
# is removed (definitely not a course name).
#
# Parameters:
#   reqlist (list of strings): list of the pre-requisite courses
# Returns: 
#   newlist (list of strings): preprocessed list of pre-requisite courses
def preprocess(reqlist):
    newlist = []

    i = 0
    while i < len(reqlist):
        # Remove all commas and brackets
        reqlist[i] = reqlist[i].replace("(", "").replace(")", "").replace(",", "")

        if ";" in reqlist[i]:
            # Treat a semicolon similar to a comma, split at the semicolon
            # and append to reqlist
            semicolsplit = reqlist[i].split(";")
            del reqlist[i]
            k = i
            for splititem in semicolsplit:
                splititem = splititem.strip()
                reqlist.insert(k, splititem)
                k += 1

        # A slash between courses indicates the same as "or". 
        # Replace all slashes with " or "
        splitslash = reqlist[i].split("/")
        if splitslash[0] != reqlist[i]:
            # There was a slash present
            j = i
            k = 0
            while k < len(splitslash):
                # Replace all slashes with "or "
                if k != 0:
                    if (splitslash[k][0:2] != "or") and (splitslash[k][0:2] != "Or"):
                        splitslash[k] = "or " + splitslash[k]
                k += 1
            # splitslash has corrected entries, replace reqlist[i] with concatenated
            # entries from splitslash
            del reqlist[i]
            while splitslash != []:
                reqlist.insert(j, splitslash[0])  # pull from start of splitslash and delete that entry
                del splitslash[0]
                j += 1

        i += 1

    j = 0
    while j < len(reqlist):
        # Must have at least 3 numbers to be the name of a course
        numcounter = parsinghelp.countNums(reqlist[j])
        if numcounter < 3:
            j += 1
            continue

        if len(reqlist[j]) > 16:
            # String is too long to be the name of a course
            j += 1
            continue

        semicolindx = reqlist[j].find(";")
        if semicolindx != -1:
            # Remove all text after a semicolon
            newlist.append(reqlist[j][0:semicolindx])
        else:
            # If no semicolon and passed the above cases, it is a valid course
            newlist.append(reqlist[j])
        
        j += 1

    return newlist
