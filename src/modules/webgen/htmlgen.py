# Authors: Jason Kim, Zachary Schmidt, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This file contains all the functions needed to generate the required
# HTML elements to produce the Program Visualizer webpage

# Dependencies: cleaner, linegen, html

from .. import cleaner
from . import linegen
import html

# Function that generates the display div which holds the plan diagram
# Parameters:
#   soup - soup object, used to create HTML tags
#   courseGroupList - list of all possible course groups taken in this program
def generateDisplayDiv(soup, courseGroupList):
    switchVariable = "selectedPlan"
    formattedCourseGroupVar="field{number}.group{number}"  # for switching between course groups
    for element in courseGroupList:
        switchVariable += "+" + formattedCourseGroupVar.format(number=element)
    return soup.new_tag("div", attrs={"class":"display",
                                      "ng-switch":switchVariable})

# Changes the header title to include deptName, which is input by
# the user in the GUI
# Parameters:
#   titleTag - "site-title" HTML tag at the top of the page
#   deptName - department name input in the GUI by the user
def switchTitle(titleTag, topTitleTag, deptName):
    titleTag.append(deptName + " Program Plan Visualizer")
    topTitleTag.append(deptName + " Visualizer")

# Places the legend for the categories of courses (math, natural sciences, design, etc.)
# Pulls the categories and colors from sequenceDict, which has these values as attributes
# Parameters:
#   legendTag - HTML tag for div which holds the category colour legend
#   categoryDict - dict mapping category to colour
#   soup - soup object, used to create HTML tags
def placeLegend(legendTag, categoryDict, soup):
    placeLegendDescription(soup, legendTag)
    placeLegendButtons(soup, legendTag, categoryDict)

# Function that places the radio inputs into the form which controls
# which plan is currently selected on the webpage
# Parameters:
#   formTag - form HTML tag where the inputs will be placed
#   courseGroupDict - dict that maps the plans to the course groups in it
#   soup - soup object, used to create HTML tags
def placeRadioInputs(formTag, courseGroupDict, soup):
    for plan in courseGroupDict:
        radioInput = soup.new_tag("input", attrs={"type":"radio", 
                                                  "name":"planselector", 
                                                  "ng-model":"selectedPlan",
                                                  "value": cleaner.cleanString(plan),
                                                  "id": cleaner.cleanString(plan)})
        labelTag = soup.new_tag("label", attrs={"for":cleaner.cleanString(plan)})
        labelTag.append(plan)
        formTag.append(radioInput)
        formTag.append(labelTag)
        breakTag = soup.new_tag("br")
        formTag.append(breakTag)

# Function that places the outer divs for the course group menu
# Parameters:
#   courseGroupSelectTag - HTML tag for outer div used to hold the course group selection menu
#   soup - soup object, used to create HTML tags
#   courseGroupDict - dict that maps plans to a dict which maps course groups to their options
def placeCourseGroupRadioInputs(courseGroupSelectTag, soup, courseGroupDict):
    for plan in courseGroupDict:
        planCourseGroupsTag = soup.new_tag("div", attrs={"id":cleaner.cleanString(plan),
                                                         "ng-switch-when":cleaner.cleanString(plan)})
        placeCourseGroupRadioInputsForPlan(planCourseGroupsTag, soup, courseGroupDict[plan])
        courseGroupSelectTag.append(planCourseGroupsTag)

# Function that places the divs for each plan
# Parameters:
#   displayTag - HTML tag for outer display div where the different plan sequences are placed
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   soup - soup object, used to create HTML tags
#   indexJS - file handle for index.js, used to write to index.js
#   controller - file handle for controller.js, used to write to controller.js
#   lineManager - line manager object, used to handle line placement and generation
def placePlanDivs(displayTag, sequenceDict, soup, indexJS, controller, lineManager):
    for plan in sequenceDict:
        switchInput = soup.new_tag("div", attrs={"id":cleaner.cleanString(plan),
                                                 "ng-switch-when":cleaner.cleanString(plan),
                                                 "style":"height:fit-content; display:flex; flex-direction:row; flex-wrap:column;"})
        placeTermsDivs(switchInput, 
                       sequenceDict[plan], 
                       soup, 
                       indexJS, 
                       controller, 
                       plan, 
                       lineManager)
        displayTag.append(switchInput)

# Function that places the description text above the category button menu
# Parameters:
#   soup - soup object, used to create HTML tags
#   legendTag - HTML tag used to hold legend
def placeLegendDescription(soup, legendTag):
    legendDescription = soup.new_tag("b", attrs={"class":"legenddescription"})
    legendDescription.append("Click on a Category Below to Highlight all Courses in that Category")
    legendTag.append(legendDescription)

# Function that places the legend buttons
# Parameters:
#   soup - soup object, used to create HTML tags
#   legendTag - HTML tag used to hold legend
#   categoryDict - dict mapping category to colour
#   with that category
def placeLegendButtons(soup, legendTag, categoryDict):
    legendBoxes = soup.new_tag("div", attrs={"class":"legendboxes"})
    for category in categoryDict:
        coursecat = placeLegendButton(soup, cleaner.cleanString(category), categoryDict[category][1])
        coursecat.append(category)
        legendBoxes.append(coursecat)
    legendTag.append(legendBoxes)

# Function that generates a button for the legend
# Parameters:
#   soup - soup object, used to create HTML tags
#   category - category for button
#   colour - colour of button
# Returns: HTML tag for category button
def placeLegendButton(soup, category, colour):
    return soup.new_tag("div", attrs={"ng-click":category+ "clickListener()", 
                                        "class":"legendbutton",
                                        "id": cleaner.cleanString(category),
                                        "style":"background-color:#" + colour})

# Function that places the course group forms for the course group selection menu
# Parameters:
#   planCourseGroupsTag - HTML tag for div that holds the group selection menu for a given plan
#   soup - soup object, used to create HTML tags
#   planCourseGroupDict - dict that maps course groups within a plan to the different options for 
#   each course group
def placeCourseGroupRadioInputsForPlan(planCourseGroupsTag, soup, planCourseGroupDict):
    for subplan in planCourseGroupDict:
        formTag = soup.new_tag("form", class_="select")
        boldFaceTag = soup.new_tag("b")
        boldFaceTag.append("Course Group " + str(subplan))
        planCourseGroupsTag.append(boldFaceTag)
        placeCourseGroupRadioInputsForSubPlan(formTag, soup, planCourseGroupDict[subplan], subplan)
        planCourseGroupsTag.append(formTag)

# Function that places the radio inputs for switching between course group options (subplans)
# Parameters:
#   subPlanTag - HTML tag for div that holds the radio inputs for that course group for
#   that specifc plan
#   soup - soup object, used to create HTML tags
#   subPlanOptionList - list of options for that course group
#   subplan - name of course group
def placeCourseGroupRadioInputsForSubPlan(subPlanTag, soup, subPlanOptionList, subplan):
    formattedSubPlanVar = "field{number}.group{number}"
    for option in subPlanOptionList:
        inputTag = soup.new_tag("input", attrs={"type":"radio",
                                                "id":option,
                                                "ng-model":formattedSubPlanVar.format(number=subplan),
                                                "value":option,
                                                "ng-change-radio":"globalSubGroupChange()"})
        labelTag = soup.new_tag("label", attrs={"for":option})
        labelTag.append(option)
        subPlanTag.append(inputTag)
        subPlanTag.append(labelTag)
        breakTag = soup.new_tag("br")
        subPlanTag.append(breakTag)

# Function that places the column flexboxes which represent the terms within a certain plan
# Parameters:
#   planTag - HTML tag for a given plan
#   planDict - dict that maps a term to a list of courses taken in that term
#   soup - soup object, used to create HTML tags
#   indexJS - file handle for index.js, used to write to index.js
#   controller - file handle for controller.js, used to write to controller.js
#   plan - name of plan whose terms are being placed
#   lineManager - line manager object, used to handle line placement and generation
def placeTermsDivs(planTag, planDict, soup, indexJS, controller, plan, lineManager):
    electiveCounterWrapper = {"ITS": 0, "PROG": 0, "COMP": 0}  # keeps track of number of electives taken in plan
    termcounter = 0  # count of number of terms placed in the plan

    for term in planDict:
        termDiv = soup.new_tag("div", attrs={"class":"term"})  # flexbox for term
        termHeader = soup.new_tag("h3", attrs={"class":"termheader"})  # title at top of term
        termHeader.append(term)
        termDiv.append(termHeader)
        placeCourses(termDiv, planDict[term], soup, controller, plan, termcounter, electiveCounterWrapper)
        planTag.append(termDiv)
        termcounter += 1
    
    # generating a list of all courses taken in this plan
    courseList = []
    for courses in planDict.values():
        courseList += courses
    # placing lines and click listeners for this plan
    linegen.placeLines(courseList, indexJS, lineManager, plan)
    linegen.placeClickListeners(courseList, controller, lineManager, plan)
    linegen.placeRightClickListeners(courseList, controller, plan)

# Function that places the course div for each individual course taken in
# one term of a given plan
# Parameters:
#   termTag - HTML tag for a given term
#   termList - list of courses being taken that term
#   soup - soup object, used to create HTML tags
#   controller - file handle for controller.js, used to write to controller.js
#   plan - name of plan whose terms are being placed
#   termcounter - which term is currently being placed (int)
def placeCourses(termTag, termList, soup, controller, plan, termcounter, electiveCountWrapper):
    courseGroupList = []  # list of courses (course objects) in a course group
    courseGroupTitle = ""  # name of the course group (eg: "Course group 2A")
    courseOrList = []  # used as temp storage for OR courses
    hexcolorlist= ["033dfc", "fc0303", "ef8c2b", "0ccb01", "bd43fa", "e8e123"]  # used to colour course group boxes
    for course in termList:
        courseID = cleaner.cleanString(course.name)+cleaner.cleanString(plan)
        courseContClass = extractCourseCategories(course)
        orCase = False
        lastOrCase = False
        if (course.calendar_print == "or") or (course.calendar_print == "lastor"):
            orCase = True
        if (course.calendar_print == "lastor"):
            lastOrCase = True
        
        if course.course_group != "":
            # add a wrapper container around course group
            courseContDiv = soup.new_tag("div", attrs={"class":"coursegroupcontainer", "style":"outline-color:#" + hexcolorlist[int(course.course_group[0])]})
            courseGroupTitle = soup.new_tag("p", attrs={"class":"coursegrouptitle"})
            courseGroupTitle.append("Course Group " + course.course_group)
        else:
            # not in a course group
            courseContDiv = soup.new_tag("div", attrs={"class":"coursecontainer"})

        # Prevent tooltip from being off screen
        courseDisc = pickTooltipSide(termcounter, courseID, soup)

        # Constructing course div, check for special cases (electives)
        if course.name == "Complementary Elective":
            # Class allows formatting so words fit in course box
            courseID = courseID+str(electiveCountWrapper["COMP"])
            courseDiv = createCourseDiv(soup, courseID, "COMP", orCase)
            # id must include which number elective it is (electiveName0, electiveName1, electiveName2, ...)
            courseDisc["id"] = courseDisc["id"][:-4] + str(electiveCountWrapper["COMP"]) + "desc"
            electiveCountWrapper["COMP"] += 1
            formatCourseDescriptionForElective(soup, course, courseDisc)

        elif course.name == "Program/Technical Elective":
            # Class allows formatting so words fit in course box
            courseID = courseID+str(electiveCountWrapper["PROG"])
            courseDiv = createCourseDiv(soup, courseID, "PROG", orCase)
            # id must include which number elective it is (electiveName0, electiveName1, electiveName2, ...)
            courseDisc["id"] = courseDisc["id"][:-4] + str(electiveCountWrapper["PROG"]) + "desc"
            electiveCountWrapper["PROG"] += 1
            formatCourseDescriptionForElective(soup, course, courseDisc)

        elif course.name == "ITS Elective":
            courseID = courseID+str(electiveCountWrapper["ITS"])
            # Class allows formatting so words fit in course box
            courseDiv = createCourseDiv(soup, courseID, "ITS", orCase)
            # id must include which number elective it is (electiveName0, electiveName1, electiveName2, ...)
            courseDisc["id"] = courseDisc["id"][:-4] + str(electiveCountWrapper["ITS"]) + "desc"
            electiveCountWrapper["ITS"] += 1
            formatCourseDescriptionForElective(soup, course, courseDisc)

        else:
            # This is a regular course. All information should be available
            courseDiv = createCourseDiv(soup, 
                                        courseID, 
                                        courseContClass, 
                                        orCase) 
            formatCourseDescriptionForRegular(soup, course, courseDisc)

        # text appearing in course box (eg: CHEM 103)
        courseHeader = soup.new_tag("h3", attrs={"class":"embed"})
        if course.elective_group != "":
              courseHeader.append("Group " + course.elective_group + " " + course.name)
        else:
            courseHeader.append(course.name)

        courseDiv.append(courseHeader)
        courseDiv.append(courseDisc)

        # flag that tells us if we should skip adding the course since it has already been added
        skipAddCourseFlag = False

        if orCase:
            # If multiple course options, append the courseDiv to a list which we will append
            # to the termTag after all options have been collected
            courseOrList.append(courseDiv)
            writeFlagsAndVariables(controller, courseID, cleaner.cleanString(plan))
            if termList.index(course) == (len(termList) - 1):
                # last course in term is an OR course, need to append to termTag immediately
                termTag, courseOrList, courseGroupList = addOrCourses(courseOrList, course.course_group, courseGroupList, termTag, soup)
                skipAddCourseFlag = True  # course has been added, don't want to add it twice
            if not lastOrCase:
                continue
            if lastOrCase and (courseOrList != []):
                # last option out of OR courses
                termTag, courseOrList, courseGroupList = addOrCourses(courseOrList, course.course_group, courseGroupList, termTag, soup)
                continue

        if course.course_group != "":
            # need to append to courseGroupList, different than check in orCase because
            # this doesn't involve OR
            courseGroupList.append(courseDiv)
            writeFlagsAndVariables(controller, courseID, cleaner.cleanString(plan))
            continue

        if not skipAddCourseFlag:
            courseContDiv.append(courseDiv) 
            termTag.append(courseContDiv)
            writeFlagsAndVariables(controller, courseID, cleaner.cleanString(plan)) 

    if courseGroupTitle != "":
        # Need to add course group title, outside of course group box so
        # append directly to termTag
        termTag.append(courseGroupTitle)
    if courseGroupList != []:
        # A course group is involved. Append each course to the coursegroupcontainer,
        # then append this container to the termTag
        for i in range(0, len(courseGroupList)):
            if i == (len(courseGroupList) - 1):
                courseGroupList[i]["class"].append("lastcourseingroup")  # last course has no bottom margin
            courseContDiv.append(courseGroupList[i])
        termTag.append(courseContDiv)

# Extracts the categories (main & sub) a course belongs to as a string
# Parameters:
#   course - Course object for an individual course
# Returns:
#   catListString - string of all categories concatenated together (space-separated)
def extractCourseCategories(course):
    catListString = cleaner.cleanString(course.main_category)
    for subcat in course.sub_categories:
        catListString += " " + cleaner.cleanString(subcat)
    return catListString

# Appends all courses in courseOrList to either termTag (if not in a course group) or to 
# courseGroupList (if in a course group)
# Parameters:
#   courseOrList - list of courseDivs of all courses to go into orcoursecontainer
#   courseGroup - course group of the current (last in OR case) course
#   courseGroupList - list of courseDivs to go into coursegroupcontainer
#   termTag - HTML tag for a given term
#   soup - soup object, used to create HTML tags
# Returns: termTag, courseOrList (cleared to be empty), courseGroupList
def addOrCourses(courseOrList, courseGroup, courseGroupList, termTag, soup):
    courseOrContDiv = soup.new_tag("div", attrs={"class":"orcoursecontainer"})  # container for all OR courses
    for i in range(0, len(courseOrList)):
        courseOrContDiv.append(courseOrList[i])  # append each OR course
        if i < (len(courseOrList) - 1):
            # Add the word "or" between courses (except not after the last option)
            courseOr = soup.new_tag("p", attrs={"class":"ortext"})
            courseOr.append("OR")  # add the word or between course boxes
            courseOrContDiv.append(courseOr)
    if courseGroup:
        # if the OR courses were in a course group, append them to courseGroupList
        # which will in turn be appended to termTag later
        courseGroupList.append(courseOrContDiv)
    else:
        # not in a course group, append directly to termTag
        termTag.append(courseOrContDiv)
    courseOrList = []  # reset in case multiple OR cases in a term

    return termTag, courseOrList, courseGroupList

# Determines which side a tooltip should appear on based on the term position on the page.
# If the term is near the left side, the tooltip appears on the right and vice versa.
# Terms 1,2 and 3 have tooltips on the right, all others on the left.
# Parameters:
#   termcounter - which term is currently being placed (int)
#   courseID - ID of the course being placed (str)
#   soup - soup object, used to create HTML tags 
# Returns:
#   courseDisc - course disc HTML tag
def pickTooltipSide(termcounter, courseID, soup):
    if termcounter < 4:
        # Term is on the left of the page, tooltip should be on right
        courseDisc = soup.new_tag("div", attrs={"id":courseID+"desc",
                                                "class":"tooltiptextright",
                                                "ng-click":"$event.stopPropagation()"})
    else:
        # Term is on the right of the page, tooltip should be on left
        courseDisc = soup.new_tag("div", attrs={"id":courseID+"desc",
                                                "class":"tooltiptextleft",
                                                "ng-click":"$event.stopPropagation()"})

    return courseDisc

# Function that constructs a course div
# Parameters:
#   soup - soup object, used to create HTML tags 
#   courseID - ID of the course being placed (str)
#   category - category of course in question
#   orBool - boolean flag for OR cases, true if course is an OR case
def createCourseDiv(soup, courseID, category, orBool):
    if orBool:
        # course is an OR case
        return soup.new_tag("div", attrs={"class":"orcourse tooltip " + category,
                                            "id": courseID,
                                            "ng-click":courseID+"Listener()",
                                            "ng-right-click":courseID+"RCListener()"})
    else:
        # course is a regular (non-OR) case
        return soup.new_tag("div",attrs= {"class":"course tooltip " + category, 
                                                "id": courseID, 
                                                "ng-click":courseID+"Listener()",
                                                "ng-right-click":courseID+"RCListener()"})

# Function that writes the flags and variables associated with a specific
# course in the JS
# Parameters:
#   controller - file handle to controller.js
#   courseID - unique ID for course
def writeFlagsAndVariables(controller, courseID, plan):
    controller.write("  var " + 
                         courseID +
                         "flag = false;\n")
    controller.write("  var " + 
                         courseID +
                         "rflag = false;\n")
    controller.write(" var " + courseID + "Time = new Date().getTime();\n")
    controller.write("this."+plan+"ClickedMap.set(\""+courseID+"\", []);\n")

# Function that constructs the course description tooltip for an elective
# Parameters:
#   soup - soup object used to create HTML tags
#   course - Course object 
#   courseDisc - course disc HTML tag
def formatCourseDescriptionForElective(soup, course, courseDisc):
    # formatting title in course description
    courseTitle = soup.new_tag("b", attrs={"class":"descriptiontitle"})
    courseTitle.append(course.name)    

    courseLine = soup.new_tag("hr", attrs={"class":"descriptionline"})

    courseDescription = soup.new_tag("p", attrs={"class":"fulldescription"})
    courseDescription.append(course.course_description)
    
    courseDisc.append(courseTitle)
    courseDisc.append(courseLine)
    courseDisc.append(courseDescription)

# Function that constructs the course description tooltip for a regular course
# Parameters:
#   soup - soup object used to create HTML tags
#   course - course object 
#   courseDisc - course disc HTML tag
def formatCourseDescriptionForRegular(soup, course, courseDisc):
    # formatting title in course description
    courseTitle = soup.new_tag("b", attrs={"class":"descriptiontitle"})
    courseTitle.append(course.name + " - " + course.long_title)

    # adding line seperating title and description
    courseLine = soup.new_tag("hr", attrs={"class":"descriptionline"})

    # adding number of credits
    courseCredits = soup.new_tag("p", attrs={"class":"descriptioncredits"})
    courseCredits.append(html.unescape("&#9733 ") + course.engineering_units + " ")

    # adding fee index
    courseFeeIndex = soup.new_tag("i", attrs={"class":"descriptionfeeindex"})
    courseFeeIndex.append("(" + "fi " + course.calc_fee_index + ")" + " ")

    # adding term avail 
    courseTermAvail = soup.new_tag("p", attrs={"class":"descriptionavailability"})
    courseTermAvail.append("(" + course.duration + ", ")

    # adding alpha hours
    courseAlphaHours = soup.new_tag("p", attrs={"class":"descriptionalphahours"})
    courseAlphaHours.append(course.alpha_hours + ")" + " ")

    # adding desc
    courseDescription = soup.new_tag("p", attrs={"class":"fulldescription"})
    courseDescription.append(course.course_description)

    # adding accreditation info
    courseAccreditationHeader = soup.new_tag("b", attrs={"class":"accreditationheader"})
    courseAccreditationHeader.append("Accreditation Units")
    courseAccreditationUnits = soup.new_tag("div", attrs={"class":"accreditationunits"})
    for accredCat in course.accredUnits:
        if course.accredUnits[accredCat] != 0:  # only display if units are not zero
            courseAccreditationUnits.append(accredCat + ": " + str(course.accredUnits[accredCat]) + " Units\n")
            courseAccreditationUnits.append(soup.new_tag("br"))

    # appending info to disc tag
    courseDisc.append(courseTitle)
    courseDisc.append(courseLine)
    courseDisc.append(courseCredits)
    courseDisc.append(courseFeeIndex)
    courseDisc.append(courseTermAvail)
    courseDisc.append(courseAlphaHours)
    courseDisc.append(courseDescription)
    courseDisc.append(soup.new_tag("br"))
    courseDisc.append(courseAccreditationHeader)
    courseDisc.append(courseAccreditationUnits)
