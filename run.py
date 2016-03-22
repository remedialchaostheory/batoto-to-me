from __future__ import print_function
import os
import sys
import time
import random
import codecs
import re
import requests
from bs4 import BeautifulSoup

# User-Agent as of 08/23/2015
headers = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0)"
                   " Gecko/20100101 Firefox/40.0"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;"
               "q=0.9,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive"
}

# Feature list:
# - Spoofs header of HTTP request as if you are using an average web browser
# - Sleeps up to 10 seconds after every HTTP request
#   (don't want to overload anyone's servers !)
# -

# TODO
# - proxy !
# - error handling
# - visual dots for loading/sleeping
# - check what chapters you have already (and maybe even what pages?? black
#   magic..) and ask you if you want to update them
# - reorder the downloading of more than one chapter (current goes descending)
# - change re.search to re.match
# - provide support for mangaeden.com
# - deploy to AWS for updates and notifications
# - add scanlator group
#   - link to their website
#   - message to user to support them
# - handle more than one english version of a chapter
# - add search function (instead of typing in URL)
# - mangaupdates.com is a good resources for latest chapters and info on
#   their scanlator groups
# - connect to mangaeden.com API (uses JSON format)
#   - integrate w/ mymanga (their personal manga list page)
# - BUG: only gets the most recent upload of a given chapter
# - BUG: HTTP request fails when also downloading on a Bittorrent client
#   (specifically Transmission on OS X)





def main():
    """
    Main function for execution. Uses given command line args or user input
        for the URLs.
    """
    ### Handles input (via command line args)
    argv = sys.argv[1:]
    if argv:
        urls = argv

    ### Handles input (via user)
    else:
        urls = ask_series()

    ### Executes connection
    for url in urls:
        print("\nProcessing {url}..".format(**locals()))
        ### To go live on the web: !!!!!!!
        front_page = get_html(url)
        sleep(3)
        ### ..live code segment ends here.

        ### For local testing..
        # with codecs.open("freezing_zero_chapters.html", "r", encoding="utf-8") as f:
        #     html = f.read()
        # front_page = html
        ### ..local testing code ends here.

        ### Gets title of manga series
        series_title = get_series_title(front_page)
        print("\n{series_title} loading..".format(**locals()))

        ### Gets current number of currently released chapters in series
        chapters = get_chapters(front_page)
        # TODO
        # - return only UNIQUE chapters
        num_chapters = len(chapters)
        chapters_avail = []

        print("\nThis series has a total of {num_chapters} chapters o_0'\n"
              "NOTE: some may be duplicated (i.e. by different scanlator "
              "groups"
              .format(**locals()))

        ### Asks user for what chapters they want
        formatted_series_title = format_filename(series_title)
        requested_ch = ask_chapters(num_chapters,
                                    series=series_title)

        ### Processes requested chapters
        download_ch_list = get_chapters(front_page, requested_ch=requested_ch)

        ### Asks/creates manga series directory
        # TODO
        # - factor this out into a separate function?
        # - ask user to create a custom directory in their "home" folder
        while True:
            default_dir = os.path.expanduser("~/Manga")

            dir_placement = raw_input(
                "\nKind sir, would you like me to place these chapter(s) of "
                "{series_title} in the default directory of '{default_dir}'\n"
                "Please reply with 'yes/no' or 'y/n'\n".format(**locals()))
            ### Forces lower case
            if not dir_placement.islower():
                dir_placement = dir_placement.lower()

            ### Handles user input of "y" or "yes"
            if dir_placement in ("y", "yes"):
                create_directory(default_dir)
                series_dir_path = (
                    default_dir + "/" + formatted_series_title)
                create_directory(series_dir_path)

                # if not os.path.exists(default_dir):
                #     print("Creating path..")
                #     os.mkdir(default_dir)
                #     ### Series path
                #     series_dir_path = (
                #         default_dir+"/"+format_filename(series_title))
                #     os.mkdir(series_dir_path)
                #     print("\nPath {series_dir_path} created."
                #           .format(**locals()))
                break

            ### Handles user input of "n" or "no"
            # TODO (in progress..)
            # - user input directory creation
            elif dir_placement in ("n", "no"):
                print("Feature coming soon to a theatre near you.. !")
                '''
                while True:
                    custom_dir = raw_input(
                        "Where would you like to put the manga in?")
                    if not os.path.exists(default_dir):
                        print("Creating custom path..")
                        ### NOTE: creates all directories needed to contain
                        ###       leaf directory
                        try:
                            os.mkdir(custom_dir)
                        except OSError:
                            print("Please enter a valid directory path")
                            continue
                        print("\nPath {custom_dir} created.".format(**locals()))
                    break
                '''
                continue

        ### Handles each requested chapter in manga series
        for chapter in download_ch_list:
            chapter_title = chapter[0]
            ### Uncomment below for LIVE online version
            chapter_url = chapter[1]
            print("\nChecking out {chapter_title}..".format(**locals()))
            ### ..live code segment ends here.

            ### Creates a directory for the current chapter
            formatted_chapter_title = format_filename(chapter_title)
            chapter_dir_path = series_dir_path + "/" + formatted_chapter_title
            create_directory(chapter_dir_path)
            # NOTE: chapter_url is also the same as the first page of
            #       the chapter from which we can get all chapter page URLs

            ### Gathers URLs of each page in current chapter
            ### Uncomment below for LIVE online version
            manga_page_html = get_html(chapter_url)
            sleep()
            all_manga_page_urls = get_all_manga_page_urls(manga_page_html)
            total_manga_pages = len(all_manga_page_urls)
            ### ..live code segment ends here.

            ### For local testing..
            # with codecs.open(
            #     "freezing_zero_vol4_ch18.html", "r", encoding="utf-8") as f:
            #     html = f.read()
            # chapter_url = "freezing_zero_chapters.html"
            # print("\njaja !",chapter_title, chapter_url)
            # all_manga_page_urls = get_all_manga_page_urls(html)
            ### ..local testing code ends here.

            ### Downloads each page of current chapter
            for page in all_manga_page_urls:
                page_num = page.split("/")[-1]
                print("\nProcessing page {page_num} of {total_manga_pages}.."
                      .format(**locals()), end="")
                # print("all manga pages:", page)
                manga_page_html = get_html(page)
                manga_page_img_url = get_manga_page_img_url(manga_page_html)
                sleep()
                download_file(manga_page_img_url, chapter_dir_path)


def sleep(start=5):
    """
    Sleeps for a random interval within 10 seconds

    Parameters:
        start (int): lower bound for time interval
    Returns:
    Raises:
    """
    while True:
        random_seconds = random.random() * 10
        random_seconds = float("%.2f" % random_seconds)
        if start < random_seconds:
            break
    print("\nquick nap for {random_seconds} seconds.. zzzz..".format(**locals()))
    time.sleep(random_seconds)


def create_directory(path):
    """
    Checks if path exists.
        If it exists, does nothing. If not, creates directory.

    Parameters:
        path (str): path to directory
    Returns:
    Raises:
    """
    if not os.path.exists(path):
        print("\nCreating path..")
        os.mkdir(path)
        print("\nPath {path} created.".format(**locals()))


def get_series_title(html):
    """
    Gets the series title from the HTML page

    Parameters:
        html (str): HTML of site
    Returns:
        series_title (str): Title of series
    Raises:
    """
    soup = BeautifulSoup(html, "html.parser")
    series_title = str(soup.find("title").contents)
    series_title = re.search("(\[u\')(.+)( \- Scan)", series_title).group(2)

    return series_title


def ask_series():
    """
    Asks user for the series URL;

    Parameters:
        None
    Returns:
        urls (list): List of URLs of all series requested
    Raises:
    """
    i = raw_input("Please enter the base URL(s) separated by commas:\n"
                  "e.g. https://bato.to/comic/_/comics/one-piece-r39\n")

    ### For multiple series
    urls = i.split(",")
    for url in urls:
        url = url.strip()

    return urls


def ask_chapters(max, series=None):
    """
    Asks user for chapter requests

    Parameters:
        max (int): total number of found chapters in series
        series (str): raw title of series
    Returns:
        requested_ch (list): List of chapter numbers requested
    Raises:
    """
    requested_ch = []
    while True:
        # TODO
        # - add selection of specific chapters (e.g. 3, 6, 15)
        answer = raw_input("\nWhich chapters do you want to download?\n"
                           "please enter one of the following:\n"
                           "  - a single chapter (e.g. '7')\n"
                           "  - a range (e.g. '34-40')\n"
                           "  - 'all'\n"
                           "  - 'most recent'\n"
                           "  - 'idk' if you're laZy and want me to check for"
                           "for you\n")

        if not answer.islower():
            answer = answer.lower()

        ### Handles a range
        match = re.search("(\d+)-(\d+)", answer)

        # TODO
        # - put if/else statements in order
        # - use a case switch flow?
        if answer == "all":
            print("\nCommencing..")
            requested_ch = range(1, max+1)
            break
        elif answer == "most recent":
            print("Stay tuned ! Feature coming soon to a theatre near you.. ")
            ### The continue statement below won't be reached
            ###     the raise statement above causes it to restart the loop?
            continue
        elif match:
            beginning_ch = int(match.group(1))
            end_ch = int(match.group(2))
            if beginning_ch <= end_ch:
                requested_ch = range(beginning_ch, end_ch+1)
                break
            else:
                print("Please enter a valid range")
                continue
        elif answer.isdigit():
            requested_ch.append(int(answer))
            break
        elif answer == "idk":
            default_dir = os.path.expanduser("~/Manga")
            while True:
                check_ans = raw_input("Should I check the default directory "
                                      "of '{default_dir}'? y/n\n"
                                      .format(**locals()))
                if check_ans == "y":
                    formatted_series = format_filename(series)
                    series_dir = default_dir + "/" + formatted_series
                    if not os.path.exists(series_dir):
                        print("Looks like we don't have anything for that "
                              "yet..")
                    else:
                        series_dir_contents = os.listdir(series_dir)
                        found_chapters = []
                        for chapter in series_dir_contents:
                            # TODO:
                            # - sort this in numerical order
                            # NOTE: matches for folders w/ "ch" or "chapter"
                            #       in them or
                            chapter_match = re.match(
                                "(ch\D{0,3})?(chapter\D{0,3})?(\d+)",
                                chapter, re.IGNORECASE).group(3)




                        if not os.path.exists(chapter_dir):
                            print("Looks like we don't have any chapters for"
                                  " that yet..")
                        # else:

### LEFT OFF HERE
                    break
                elif check_ans == "n":
                    print("Sorry, we are currently working hard on this"
                          " feature.. come back again soon !")
                    # custom_check = raw_input("Please list the path:\n")
                    # if
                    continue

        else:
            print("Come again?? I didn't hear you right..")
            continue

    return requested_ch


def get_html(url):
    """
    Connects to given URL and also lists any redirection.

    Parameters:
        url (str):
    Returns:
        content (str): HTML of the URL

    Raises:

    """
    r = requests.get(url, headers=headers, verify=True)
    # Handle redirections
    if r.history:
        print("\nRequest was redirected:")
        for resp in r.history:
            print(resp.status_code, resp.url)
        print("\nFinal destination:")
        print(r.status_code, r.url)

    # print("Status code:", r.status_code)
    # print("Page header:", r.headers)
    # print("My header:", r.request.headers)

    content = r.content.decode("utf-8")

    """
    My first attempt:
    Didn't work because I was trying to use Session(). Still not sure
        how to use it
    """
    # with requests.Session() as s:
    #     s.get(url, headers=headers, verify=True)
    #     print("Connected !")
    #     print("s.headers : {}".format(s.headers))
    #     print("status code: %s" s.status_code)
    #     # print("s.request.headers : %s" % s.request(headers))

    return content


def download_file(url, dir_path):
    """
    Downloads file from the given URL.

    Parameters:
        url (str):
    Returns:

    Raises:
    """
    local_filename = url.split("/")[-1]
    # print("\nDownloading.. %s" % local_filename)
    print("Downloading.. {local_filename}.. ".format(**locals()), end="")
    dl_destination = dir_path + "/" + local_filename
    if not os.path.exists(dl_destination):
        r = requests.get(url, headers=headers, verify=True, stream=True)
        if r.status_code == 200:
            # with codecs.open(dl_destination, "wb", encoding="utf-8") as f:
            with codecs.open(dl_destination, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        else:
            print("Status code not 200 /:\n"
                  "wonder if we should try again..")
    else:
        print("\nwoops ! already have this page..")

    print("fin !")


def format_filename(string):
    """
    Converts a string to an acceptable filename
        e.g. "Go! series - F1" into "Go_series_-_F1"

    Parameters:
        string (str): raw filename
    Returns:
        formatted_filename (str): formatted filename
    Raises:
    """
    # NOTE: Periods (.) and dashes (-) are allowed
    #       Spaces are converted to dashes
    formatted_filename = []
    symbols = "!@#$%^&*()+=[]\{}|:\";'<>?,/'"
    for c in string:
        if c == " ":
            formatted_filename.append("_")
        elif c in symbols:
            pass
        else:
            formatted_filename.append(c)

    formatted_filename = "".join(formatted_filename)

    return formatted_filename


def get_chapters(manga_series_html, requested_ch=None):
    """
    Takes HTML of a Batoto manga series page:
        e.g. https://bato.to/comic/_/comics/tokyo-ghoul-r3056

    Parameters:
        manga_series_html (str): HTML of manga series
        requested_ch (list): list of requested chapters
    Returns:
        chapter_list (list): List of manga chapters w/
            sub-list of formatted title filename, URL
            e.g [
        ["Tokyo_Ghoul_Vol_1_-_Ch_1",
         "http://bato.to/read/_/67864/tokyo-ghoul_v1_ch1_by_lazy-ass-scans"],
        ["Tokyo_Ghoul_Vol_1_-_Ch_2",
         "http://bato.to/read/_/78373/tokyo-ghoul_v1_ch2_by_lazy-ass-scans"]
        ]
        NOTE: Order is in reverse (extracted directly from HTML which has them
              in descending order)
    Raises:
    """

    chapter_list = []
    soup = BeautifulSoup(manga_series_html, "html.parser")

    ### Don't think this is needed. Already sort of factored out
    ###     series_title
    # TODO:
    # - refactor the 2 following lines:
    #   (series_title is already in get_series_title() but don't want to
    #   parse the whole HTML content again)
    # series_title = str(soup.find("title").contents)
    # series_title = re.search("(\[u\')(.+)( \- Scan)", series_title).group(2)
    # series_dir = format_filename(series_title)

    print("\nGathering chapters..")
    # print("Files will be saved in this directory:", series_dir)

    ### Main body of scraper
    ### Gets chapter title and URL
    ### NOTE: only english
    keyword = "lang_English"
    # print("\nMatches in class_ of \"%s\":" % keyword)
    # print("\nFound these chapters:")
    matches = soup.find_all(class_=re.compile(keyword))
    total_chapters = len(matches)
    # print("total chapters", total_chapters)
    # print("requested_ch", requested_ch)

    ### Prints which chapters to process
    # if requested_ch == None:
    if not requested_ch:
        requested_ch = range(1, total_chapters+1)
        print("Retrieving ALL chapters (total: {total_chapters})"
              .format(**locals()))
    else:
        print("Retrieving the following chapters:", requested_ch)

    done = []
    for match in matches:
        ### Prints whole match
        # print("\n", match)

        ### Finds chapter number
        title = match.a.get("title")
        # print("title ", title)
        chapter_match = re.search("(Ch.)(\d+).?(\d+)?", title)
        # print("chapter match ", chapter_match)
        if chapter_match.group(2):
            chapter_num = int(chapter_match.group(2))
        if chapter_match.group(3):
            chapter_num_extra = int(chapter_match.group(3))
            whole_chapter_num = float(
                str(chapter_num) + "." + str(chapter_num_extra))
        else:
            whole_chapter_num = chapter_num

        # print("chapter_num", chapter_num)

        ### Processes/formats chapters
        if (chapter_num in requested_ch and
            whole_chapter_num not in done):
            # print()
            # print("match.a.get", title)
            title = title.split(" |", 1)[0]
            # print("title.split", title)
            # formatted_title = format_filename(title)
            # print("formatted title", formatted_title)
            url = match.a.get("href")
            # old
            # chapter_list.append([title, url])
            chapter_list.insert(0, [title, url])
            done.append(whole_chapter_num)

            ### For debugging:
            # print("title:", title) # WORKS !!!!!!!!!!!
            # print("URL:", url) # WORKS !!!!!!!!!!!

    return chapter_list


def get_manga_page_img_url(manga_ch_page_html):
    """
    Gets the image URL of a Batoto manga chapter page:
        e.g. https://bato.to/read/_/67864/tokyo-ghoul_v1_ch1_by_lazy-ass-scans

    Parameters:
        manga_ch_page_html (str): HTML of Batoto manga chapter page
    Returns:
        img_urls (str): image URL of manga chapter page
    Raises:
    """
    soup = BeautifulSoup(manga_ch_page_html, "html.parser")

    manga_page = soup.find_all("img", id="comic_page")
    ### For debugging:
    # print("\nFind all img id=comic_page:")

    try:
        len(manga_page) == 1
    except ValueError:
        print("Not sure why, but there's more than one image here??")

    img_urls = []
    for page in manga_page:
        ### Prints raw soup object
        # print(page)
        title = page.get("alt")
        url = page.get("src")
        img_urls.append(url)

        ### For debugging:
        print("\nFound: [ {title} ]".format(**locals()), end="")
        # print("at:", url)

    return img_urls[0]


def get_all_manga_page_urls(manga_page_html):
    """
    Gets ALL of the Batoto manga chapter page URLs from ANY chapter page:
        e.g. https://bato.to/read/_/67864/tokyo-ghoul_v1_ch1_by_lazy-ass-scans
             https://bato.to/read/_/67864/tokyo-ghoul_v1_ch1_by_lazy-ass-scans/2

    Parameters:
        manga_page_html (str): HTML of ANY Batoto manga chapter page
    Returns:
        all_manga_ch_pg_urls (list): URLs of ALL manga chapter pages
    Raises:
    """
    all_manga_ch_pg_urls = []
    soup = BeautifulSoup(manga_page_html, "html.parser")

    print("\nFlipping through chapter to see number of pages..")

    raw_pages = soup.find("select", id="page_select")

    ### For debugging:
    # print("\nfind all select, id=page_select:")
    # print("select.option")
    # print(raw_pages.option)
    # print("select.find_all(option)")
    # print(raw_pages.find_all("option"))
    # print("select.find_all(option)")
    # print(raw_pages.find_all("option"))

    pages = raw_pages.find_all("option")
    for page in pages:
        url = page.get("value").encode("utf-8")
        all_manga_ch_pg_urls.append(url)

    num_chapters = len(all_manga_ch_pg_urls)
    print("Found {num_chapters} chapters ! awesomee".format(**locals()))

    return all_manga_ch_pg_urls


if __name__ == "__main__":
    main()

    """Testing Suite"""
    # download_file("https://upload.wikimedia.org/wikipedia/meta/6/6d/Wikipedia_wordmark_1x.png")

    ### From URL
    # html = get_html("https://en.wikipedia.org/wiki/Claudia_Cohen")
    # print scrape(html).encode("utf-8")

    ### From local file: chapters
    ### For local testing..
    # with codecs.open("freezing_zero_chapters.html", "r", encoding="utf-8") as f:
    #     html = f.read()
    # ch = range(2, 5)
    ### Test a range:
    # get_chapters(html, requested_ch=ch)
    ### Test ALL chapters:
    # get_chapters(html)
    ### ..local testing code ends here.

    ### From local file: pages
    ### For local testing..
    # with codecs.open("freezing_zero_vol4_ch18.html", "r",
    #                  encoding="utf-8") as f:
    #     html = f.read()
    # get_manga_page_img_url(html)
    # get_all_manga_page_urls(html)
    ### ..local testing code ends here.

    # print scrape(html).encode("utf-8")

