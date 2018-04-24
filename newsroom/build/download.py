import time, random, requests
from concurrent.futures import ThreadPoolExecutor


class Downloader(object):

    def __init__(

            self,
            workers = 8,
            tries = 3,
            sleep = 2,
            multiplier = 1.5,

            ):

        """

        Launch a thread pool of workers to download a list of URLs
        asynchronously, with built-in adjustable rate limiting.

        Arguments:

            - workers: the number of threads to launch (default = 8)
            - tries: download attempts to make after a failure (default = 3)
            - sleep: approx thread wait time between downloads (default = 2)
                * (approximate rate is workers/sleep URLs per second)
            - multiplier: increase sleep time on each try (default = 1.5)

        Example:

            >>> ts = Downloader(workers = 12)
            >>> results = ts.download(["youtube.com"])

        """

        self.workers = workers
        self.tries = tries
        self.sleep = sleep
        self.multiplier = multiplier


    def download(self, urls):

        """

        Download a thing.

        """

        urls = list(urls)

        with ThreadPoolExecutor(self.workers) as executor:

            yield from executor.map(self._thread, urls)


    def _thread(self, url):

        sleep = self.sleep

        for _ in range(self.tries):

            time.sleep(random.random() * sleep * 2)

            try:

                req = requests.get(url)

                if req.status_code == 200:

                    return {
                        "url": url,
                        "html": req.text
                    }

                else:

                    raise Exception()

            except Exception:

                sleep *= self.multiplier

        return None
