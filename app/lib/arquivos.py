import os


def apagar(*arquivos):

    for arq in arquivos:

        try:

            os.remove(arq)

        except:

            pass
