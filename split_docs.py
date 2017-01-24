import re


interesting_markers = ['.I', '.T', '.W', '.A', 'K']
markers = ['.I', '.T', '.W', '.B', '.A', '.N', '.X', '.K']


def is_marker(line_begin):
    return line_begin in markers


def is_interesting_marker(line_begin):
    return line_begin in interesting_markers

doc_counter = 0
storing = False
temp = ""
with open("cacm.all") as cacm_file:
    for line in cacm_file:
        line_begin = line[0:2]
        if not is_marker(line_begin):
            if storing:
                for word in filter(None, re.split('[^a-zA-Z\d:]', line)):
                    temp += word.lower() + " "
        else:
            if is_interesting_marker(line_begin):
                if line_begin == '.I' and temp != "":
                    doc_counter += 1
                    with open("cacm-data/0/CACM-%s.html" % doc_counter, 'w') as doc_file:
                        doc_file.write(temp)
                    temp = ""
                storing = True
            else:
                storing = False
