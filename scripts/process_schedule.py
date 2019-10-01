import cgi
import os
import cgitb

cgitb.enable()
form = cgi.FieldStorage()

fileitem = form['scheduleFile']
# Test if the file was uploaded
# if fileitem.filename:
#     strip leading path from file name to avoid
#     directory traversal attacks
    # fn = os.path.basename(fileitem.filename)
    # open('/tmp/' + fn, 'wb').write(fileitem.file.read())
    # message = 'The file "' + fn + '" was uploaded successfully'
#
# else:
#     message = 'No file was uploaded'
