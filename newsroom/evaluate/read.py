import fcntl, time, os


def readiter(output):

    # Adapted from:
    # https://gist.github.com/sebclaeys/1232088

    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    while True:

        text = output.read()

        if text is not None:

            text = text.decode("utf-8").strip()
            if text == "": break
            yield text

        else:

            time.sleep(0.001)
