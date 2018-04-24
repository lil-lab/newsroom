import re

from urllib.parse import quote, urlparse, urljoin
from bs4 import BeautifulSoup
from readability import Document


_whitespace = re.compile(r"\s+")


class Article(object):

    """

    Reads in a {url: "", html: ""} archive entry from the downloader script.
    This will scrape the provided HTML and extract the summary and text. Note
    that the provided URL in this case is actually the ARCHIVE url (Maybe this
    should be made clearer in the downloader script?).

    """

    def __init__(self, archive, html):

        self.archive = archive
        self.html    = html if html is not None else ""

        self._parse_archive()
        self._parse_html()



    def _parse_archive(self):

        *splits, url = self.archive.split("id_/")
        *_, date = splits[0].split("/")

        self.url  = self.normalize_url(url)
        self.date = date


    def _parse_html(self):

        self._load_html()
        self._find_canonical_url()

        self._extract_text()
        self._extract_summary()


    def _extract_summary(self):

        self.all_summaries = {}

        for meta in self.soup.findAll("meta"):
            for attr, value in meta.attrs.items():

                if attr in ("name", "property") and "description" in value:

                    # Extract the tag content. If we can't find anything,
                    # ignore it and move onto the next tag.

                    try:

                        self.all_summaries[value] = meta.get("content").strip()

                    except Exception:

                        continue

        if len(self.all_summaries) == 0:

            self.summary = None
            return


        for kind in ("og:description", "twitter:description", "description"):

            if kind in self.all_summaries:

                self.summary = self.all_summaries[kind]
                break

        else:

            random_pick = sorted(self.all_summaries)[0]
            self.summary = self.all_summaries[random_pick]


    def _extract_text(self):

        """

        Uses Readability to extract the body text and titles of the articles.

        """

        # Confusingly, the Readability package calls the body text of the article
        # its "summary." We want to create a plain text document from the body text,
        # so we need to extract the text from Readability's HTML version.

        body_soup = BeautifulSoup(self.readability.summary(), "lxml")


        # Now go through and extract each paragraph (in order).

        paragraph_text = []
        for paragraph in body_soup.findAll("p"):

            # Very short pieces of text tend not to be article body text, but
            # captions, attributions, and advertising. It seems that excluding
            # paragraphs shorter than five words removes most of this.

            if len(paragraph.text.split()) >= 5:

                paragraph_body = _whitespace.sub(" ", paragraph.text).strip()
                paragraph_text.append(paragraph_body)


        # We join the plain text paragraphs of the article with double new lines.

        self.text = "\n\n".join(paragraph_text)


        # "Short title" uses in-page heuristics to remove cruft from <title>; e.g.:
        # .title():       American Recalls Moment Leg Broken by Truck in Nice - ABC News
        # .short_title(): American Recalls Moment Leg Broken by Truck in Nice

        self.title = self.readability.short_title()


    def _load_html(self):

        # Readability crashes if it encounters empty pages.

        if self.html.strip() == "":

            raise Exception("No page content?")

        # The document has content. Create:
        # - A Readability parse object to extract the text
        # - A full-page BeautifulSoup object to extract summaries.

        self.readability = Document(self.html)
        self.soup = BeautifulSoup(self.html, "lxml")


    def _find_canonical_url(self):

        # Start out by normalizing the URL as we know it. Without reading the
        # page yet, this is our best guess of the article's canonical URL.

        self.original_url = self.url

        try:

            # Try to extract the page's canonical URL, if it has one. If it doesn't,
            # BeautifulSoup will raise an exception, and we will give up, sticking
            # with the normalized URL as the best URL.

            rel_canon = self.soup.find("link", {"rel": "canonical"}).get("href")


            # I've sometimes seen the canonical URL be relative to the current page.
            # Although this is rare, we can handle this using our best knowledge of
            # the page's URL so far. Just in case, we'll normalize this too.

            abs_canon_url = urljoin(self.url, rel_canon)
            norm_canon_url = self.normalize_url(abs_canon_url)


            # Sometimes, the canonical URL will be on a completely different domain.
            # I'm not sure why. But as a sanity check, make sure it's on the same
            # domain before using it.

            if self.same_domain(self.url, norm_canon_url):

                self.url = self.norm_canon_url

        except Exception:

            # If we've failed at some point (most likely because the page doesn't
            # use the canonical tag), set the canonical and normalized canonical
            # URLs to None so that the user is aware of this.

            pass


    def serialize(self):

        """

        Return simple page object to JSONify and write to file.

        """

        return {
            "url":     self.url,
            "archive": self.archive,
            "title":   self.title,
            "date":    self.date,
            "text":    self.text,
            "summary": self.summary
        }


    @staticmethod
    def process(page):

        url = page.get("archive", page.get("url"))
        html = page.get("html", "")
        if html is None: html = ""

        try:
            return Article(url, html).serialize()
        except:
            return None


    @staticmethod
    def same_domain(url1, url2):

        """

        Check if two URLs share the same domain (urlparse netloc).
        This is used primarily in evaluating canonical URLs.

        """

        return urlparse(url1).netloc == urlparse(url2).netloc


    @staticmethod
    def normalize_url(url):

        """

        Remove fragments, ports, and other junk from Archive.org scrapes.
        This is to detect duplicate pages, and prettify URLs.

        """

        # Multiple forward slashes should be replaced with just one.

        cleaned = url.replace("://", "\0") \
                     .replace("//", "/") \
                     .replace("\0", "://")

        # Removing fragments and query parameters.

        parsed = urlparse(cleaned)
        parsed = parsed._replace(path = quote(parsed.path, safe = "%/"),
                                 netloc = parsed.netloc.replace(":80", ""),
                                 query = "", fragment = "")

        return parsed.geturl()
