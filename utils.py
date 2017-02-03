from os.path import dirname, exists
from os import makedirs


def make_dirs(filepath):
    basedir = dirname(filepath)
    if not exists(basedir):
        makedirs(basedir)


def load_map(map_path, key_type=str, value_type=str):
    result = dict()
    with open(map_path) as map_file:
        for line in map_file:
            temp = line.split(" : ")
            key = key_type(temp[0])
            result[key] = value_type(temp[1][:-1])
    return result


def save_map(m_map, file_path):
    with open(file_path, 'w') as map_file:
        for key in m_map:
            map_file.write("%s : %s\n" % (key, m_map[key]))


def term_indexes_to_file_lines(term_indexes):
    return [term_index_to_file_line(term_index) for term_index in term_indexes]


def term_index_to_file_line(term_index):
    term_id, occurrences = term_index
    result = "%s:" % term_id
    for occurrence in occurrences:
        result += "%s|" % str(occurrence)[1:-1]
    return result[:-1] + "\n"


def file_lines_to_term_indexes(lines):
    return [file_line_to_term_index(line) for line in lines]


def file_line_to_term_index(line, refined=False):
    temp = line[:-1].split(':')
    term_id = int(temp[0])
    str_occurrences = temp[1].split('|')
    occurrences = list()
    for str_occurrence in str_occurrences:
        temp = str_occurrence.split(',')
        occurrences.append((int(temp[0]), int(temp[1]), float(temp[2])) if refined else (int(temp[0]), int(temp[1])))
    return term_id, occurrences
