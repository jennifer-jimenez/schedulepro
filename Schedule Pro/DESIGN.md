# Design

## Login
The first screen to pop up upon loading the website is the login page.
It prompts the user for a username and password. If either/both of the input
fields are left blank, then the alert's message changes correspondingly. If
an invalid username password combination is input, the alert also lets the user know.
From this first screen you can access a register page through the navbar, so that
users without an existing account can make one.

## Register
The register page prompts the user for a username, password, and a confirmation of the password.
Upon pressing the submit button, the user will automatically be logged in if the account creation
was successful. If the user leaves any of the fields blank, mistypes the confirmation of the
password, or tries to create an account with a username that already exists, then the alert's
message will update accordingly.

## Index
The index page contains a section for the "Weekly Schedule", initially an empty table with only days of
the week as the header, as well as a "Random Tasks" section, also initially empty. There is an "add a task"
link in the header that redirects the users to a page with a form. The empty placeholders on the index
page will be populated based on the information input into this form. Upon pressing the "Optimize" button
at the bottom of the page, the optimize route in application.py will be called, which contains the
"get_distance" and "optimize" functions. Based on the calculations made by these functions, the random
tasks will accordingly be inserted into the weekly schedule. Accordingly, in this case, means by closest
location.
** Optimize Route **
The get_distance() function uses the Google Maps Distance Matrix API to calculate the distance of any two location
passed into it. Syntax has been derived from the documentation of this API.

The closest() function recieves a location from the any time tasks, as well as a list of the non-negotiable
locations as arguments. It loops through this list, calling the get_distance() function for each location
comparison. The distance is returned by the function, which is then compared to a variable "shortest" that stores the
value of the current shortest distance. If the new calculation is less than the current shortest value, then it is
replaced, and a variable called "closestloc" is updated to store the non-negotiable task location that was just compared
(which was found to be the shortest distance).

Based on the location the closest() function returns, the any time task is inserted into a list containing all of
the non-negotiable tasks. It is inserted after the closest location is visited. The any time task is given
a "starttime" attribute equivalent to the "endtime" of that previous non-negotiable task, and an "endtime"
attribute that is 20 minutes from its "starttime." The any time task is only inserted if the weekday the closest
location is visited is before the deadline specified for that any time task.

## New
This page contains a form that will get all the info for tasks the user will enter. It initially
displays a "Title" and "Location" field, as well as radio buttons for the user to identify if
the task they are about to enter is non-negotiable (e.g. class, work, meeting), or if it is a task you
can complete at any time (e.g. bank, shipping center). If it is non-negotiable, a javascript function
displays "Weekday," "Start Time," and "End Time" fields. If it is an anytime task, the javascript
function prompts the user for a deadline for the task. Tasks are inserted into separate SQL tables
based on the type of task.

Non-negotiable tasks are inserted into the weekly schedule in the index page accordingly, sorted by
the start time of each task of the day. Anytime tasks are added to the page as bootstrap cards.

The weekday is inserted as a corresponding number, in order to be able to check if the deadline of a
task is greater than (occurs after) the date it is to be inserted into.

## Drop
A simple page meant for deleting a task from the SQL table, and consequently removing it from the
index page. You will be redirected to this page upon clicking on any task, whether in the weekly
schedule or random tasks section. From there, the task's name pops up with a delete button under it,
which upon clicking runs a SQL command that deletes the task from the table. You are redirected to
the index page where that task no longer exists.

## Apology
A simple page that displays "Oops! Something went wrong." should an internal server error occur.
There is a button that redirects you to the login page.
