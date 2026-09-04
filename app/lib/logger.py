from datetime import datetime


def info(msg):

    print(
        f"[{datetime.now()}] {msg}"
    )


def erro(msg):

    print(
        f"[ERRO] {datetime.now()} {msg}"
    )
