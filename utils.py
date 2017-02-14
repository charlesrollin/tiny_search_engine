import struct
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


def save_positions(positions, file_path):
    with open(file_path, 'w') as positions_file:
        for position in positions:
            positions_file.write("%i\n" % position)


def term_index_to_bin(term_index, refined=False):
    bin_format = '2if' if refined else '2i'
    result = struct.pack('i', term_index[0])
    for posting in term_index[1]:
        result += struct.pack(bin_format, *posting)
    return result


def bin_to_term_index(raw_bin, refined=False):
    bin_format = '2if' if refined else '2i'
    term_id = struct.unpack_from('i', raw_bin)[0]
    occurrences = list(struct.iter_unpack(bin_format, raw_bin[4:]))
    return term_id, occurrences
