import tempfile
import os


def pasta_temp():

    return tempfile.gettempdir()


def arquivo(nome):

    return os.path.join(
        tempfile.gettempdir(),
        nome
    )
