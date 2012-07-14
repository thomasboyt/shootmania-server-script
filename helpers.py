import string


# remove unicode
def sanitize(s):
    filtered_string = filter(lambda x: x in string.printable, s)
    return filtered_string
