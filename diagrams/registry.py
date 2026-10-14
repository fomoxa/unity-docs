DIAGRAMS = {}


def diagram(name):
    def register(function):
        DIAGRAMS[name] = function
        return function

    return register


def pick(language, english, vietnamese):
    return vietnamese if language == 'vi' else english
