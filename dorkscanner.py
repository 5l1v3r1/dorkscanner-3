#!/usr/bin/python3
import os
import sys
import signal
import requests
import argparse
from random import randint
from functools import partial
from multiprocessing import Pool
from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup
from progress.bar import ShadyBar


line = 0
page = 0
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"
}

ASK = {
    "base_url": "https://www.ask.com/web",
    "headers": headers,
    "params": {"q": line, "page": page},
    "soup_tag": "div",
    "soup_class": {
        "class": "PartialSearchResults-item-url PartialSearchResults-item-top-url"
    },
}

BING = {
    "base_url": "https://www.bing.com/search",
    "headers": headers,
    "params": {"q": line, "first": page * 10 + 1},
    "soup_tag": "cite",
    "soup_class": "",
}

WOW = {
    "base_url": "https://www.wow.com/search",
    "headers": headers,
    "params": {"q": line, "b": page * 8},
    "soup_tag": "span",
    "soup_class": {"class": "fz-ms fw-m fc-12th wr-bw lh-17"},
}


GREEN, RED, ORANGE, PURPLE, CYAN, WHITE, YELLOW = (
    "\033[1;32m",
    "\033[91m",
    "\033[0;33m",
    "\033[0;35m",
    "\033[0;36m",
    "\033[1;37m",
    "\033[0;33m",
)
colours = [ORANGE, PURPLE, CYAN, WHITE, YELLOW]
color = colours[randint(0, 4)]


def get_arguments():
    parser = argparse.ArgumentParser(
        prog="python3 dorkscanner.py",
        description="Example : python3 dorkscanner.py -e Bing -p 2 -P 1 -o test.txt -d dorks.txt",
    )
    parser.add_argument(
        "-q",
        "--query",
        dest="query",
        help="Specifies the query",
    )
    parser.add_argument(
        "-e",
        "--engine",
        dest="engine",
        help="Specifies the search engine (Ask | Bing | WoW)",
    )
    parser.add_argument(
        "-p", "--pages", dest="pages", help="Specifies the pages numbers (Default: 1)"
    )
    parser.add_argument(
        "-P",
        "--processes",
        dest="processes",
        help="Specifies the number of processes (Default: 2)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help=f"Specifies the output file name \n(Default: {os.getcwd()}/pages/pages.txt)",
    )
    parser.add_argument(
        "-d",
        "--dork",
        dest="dork",
        help=f"Specifies the file containing the dorks (Default: {os.getcwd()}/dorks/dorks.txt)",
    )
    options = parser.parse_args()
    return options


def kill(pool=1):
    for i in range(int(options.processes)):
        pool.close()
    pool.terminate()
    print("\nThank you for using this program !")
    signal.signal(signal.SIGKILL, sys.exit(1))


def search(query, engine, page):
    counter = 0
    result = []
    params = engine["params"]
    params["page"] = page
    base_url = engine["base_url"]
    headers = engine["headers"]
    souper = engine["soup_tag"], engine["soup_class"]
    if options.dork:
        dorksfile = os.getcwd() + "/dorks/" + options.dork

        try:
            file = open(dorksfile, "r", encoding="utf8", errors="ignore")
            lines = file.readlines()
            bar = ShadyBar(f"[!] Please wait - Requests performed :", max=len(lines))
            for line in lines:
                params["q"] = line
                resp = requests.get(base_url, params=params, headers=headers)
                if "ranParachuteScript" in resp.text:
                    error = print(RED + "[¤] Bing blocks our requests")
                    print(RED + "[¤] Please use another search engine")
                    kill(pool)
                soup = bsoup(resp.text, "html.parser")
                links = soup.findAll(souper)
                counter += 1
                bar.next()
                for link in links:
                    result.append(link.text)
            bar.finish()
            return result

        except FileNotFoundError:
            print(
                f"Check that the file {options.dork} is located in the /dorks/ folder"
            )
    else:
        resp = requests.get(base_url, params=params, headers=headers)
        soup = bsoup(resp.text, "html.parser")
        links = soup.findAll(souper)
        for link in links:
            result.append(link.text)
        return result


def search_result(q, engine, pages, processes, result, output):
    blacklist = [
        "facebook",
        "google",
        "pastebin",
        "gist",
        "github",
        "udemy",
        "jetbrains",
        "youtube",
        "whatsapp",
        "telegram",
        "twitter",
        "vuldb",
        "tenable",
        "exploit-db",
        "stackoverflow",
        "bing",
        "w3schools",
        "wikipedia",
        "cvedetails",
        "exploitdb",
    ]

    if not q:
        q = "from " + options.dork

    pagesfolder = os.getcwd() + "/pages/"
    page = pagesfolder + output
    ls = []
    print("-" * 70)
    print(f"Search : {q} in {pages} page(s) on {engine} with {processes} processes")
    print("-" * 70)
    print()
    counter = 0
    for range in result:
        try:
            for r in range:
                f = open(page, "a", encoding="utf8", errors="ignore")
                if ("?" in r and "=" in r and "..." not in r and "," not in r and ":" not in r):
                    for link in blacklist:
                        if link not in result:
                            if link not in r:
                                f.write(r + "\n")
                                print(color + "[+] " + r + "\n")
                                counter += 1
                                break
                f.close()
        except:
            print("No results found")
            sys.exit(0)
    with open(page, "r") as f:
        for line in f:
            if line not in ls and "?" in line and "=" in line:
                for i in blacklist:
                    if i in line:
                        break
                ls.append(line)
    with open(page, "w") as f:
        for line in ls:
            f.write(line)
    print()
    print("-" * 70)
    print(f"No. of URLs : {counter}")
    print("-" * 70)
    print(f"Successfully created output file : {page}")


def is_internet_available():
    try:
        ping = urlopen("http://www.google.com", timeout=5000)
        return GREEN + "[!] Internet connection: OK !"
    except:
        print(RED + "[!] Internet connection: NOT OK !\n")
        sys.exit(0)


def main():

    print(is_internet_available())

    if not options.pages:
        pages = 1
    else:
        pages = options.pages

    if not options.processes:
        processes = 2
    else:
        processes = options.processes
    pool = Pool(int(processes))
    if not options.output:
        output = "pages.txt"
    else:
        output = options.output
    if not options.dork:
        dork = "dorks.txt"
    else:
        print("[!] Searching for URLs can take a few minutes with the -d option")

    if not options.query and not options.dork:
        query = input("[?] Enter your query : ")
    else:
        query = options.query
    if not options.engine:
        engine = input("[?] : Choose your search engine (Ask | Bing | WoW) : ")
    else:
        engine = options.engine

    if engine.lower() == "ask":
        options.engine = ASK
        target = partial(search, query, options.engine)
    elif engine.lower() == "bing":
        options.engine = BING
        target = partial(search, query, options.engine)
    elif engine.lower() == "wow":
        options.engine = WOW
        target = partial(search, query, options.engine)
    else:
        print("[-] The option is invalid !...")
        print("[-] Closing the program....")
        sys.exit(0)
    with pool as p:
        result = p.map(target, range(int(pages)))
        print(options.query)
    search_result(query, engine, pages, processes, result, output)


banner = """ 

    ·▄▄▄▄        ▄▄▄  ▄ •▄     .▄▄ ·  ▄▄·  ▄▄▄·  ▐ ▄  ▐ ▄ ▄▄▄ .▄▄▄  
    ██▪ ██ ▪     ▀▄ █·█▌▄▌▪    ▐█ ▀. ▐█ ▌▪▐█ ▀█ •█▌▐█•█▌▐█▀▄.▀·▀▄ █·
    ▐█· ▐█▌ ▄█▀▄ ▐▀▀▄ ▐▀▀▄·    ▄▀▀▀█▄██ ▄▄▄█▀▀█ ▐█▐▐▌▐█▐▐▌▐▀▀▪▄▐▀▀▄ 
    ██. ██ ▐█▌.▐▌▐█•█▌▐█.█▌    ▐█▄▪▐█▐███▌▐█ ▪▐▌██▐█▌██▐█▌▐█▄▄▌▐█•█▌
    ▀▀▀▀▀•  ▀█▄▀▪.▀  ▀·▀  ▀     ▀▀▀▀ ·▀▀▀  ▀  ▀ ▀▀ █▪▀▀ █▪ ▀▀▀ .▀  ▀
    
                Made By : Chocapik (https://github.com/Chocapikk)
                *** *  * ** * ** * *** *  * ** * ** * *** ** * *
                *    *      * *  *  *    *      * *  * *    * * 
                   *   *   *        *   *   *       *   *   *  
                 *         *    *        *         *    *
                     *    *   *     *    *   * *  *    *   * 
                            *      *     *       *       *   
"""

options = get_arguments()

print(color + banner)

try:
    main()
    if options.query and options.engine:
        sys.exit(0)
except KeyboardInterrupt:
    signal.signal(signal.SIGKILL, sys.exit(1))
except TimeoutError:
    print(RED + "\n[-] Too many requests, try again later ....")
    sys.exit(0)
