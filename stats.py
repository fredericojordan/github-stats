import asyncio
import os

import aiohttp
import requests
from bs4 import BeautifulSoup
from flask import Flask, make_response

ASYNC = True
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "secret_l801#+#a&^1mz)_p&qyq51j51@20_74c-xi%&i)b*u_dt^2=2key"
)
global_ranking = []


def parse_contribuition_count(html_page):
    return int(
        BeautifulSoup(html_page, "html.parser")
        .find("div", {"class": "js-yearly-contributions"})
        .text.strip()
        .split()[0]
        .replace(",", "")
    )


def get_contributions_page_sync(github_username):
    url = f"https://github.com/users/{github_username}/contributions"
    response = requests.get(url)
    return response.content


def get_contribution_count_sync(github_username):
    html_page = get_contributions_page_sync(github_username)
    return parse_contribuition_count(html_page)


def main_sync(github_usernames):
    contributions = {
        github_username: {"contributions": get_contribution_count_sync(github_username)}
        for github_username in github_usernames
    }
    ranking = sorted(
        contributions.items(), key=lambda x: x[1]["contributions"], reverse=True
    )
    for i, c in enumerate(ranking):
        print(f"{i+1}. ({c[1]['contributions']}) {c[0]}")


async def get_contributions_page_async(session, github_username):
    url = f"https://github.com/users/{github_username}/contributions"
    async with session.get(url) as response:
        return await response.text()


async def main_async(github_usernames):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for username in github_usernames:
            tasks.append(get_contributions_page_async(session, username))
        profile_pages = await asyncio.gather(*tasks)

        contributions = [
            parse_contribuition_count(html_page) for html_page in profile_pages
        ]
        contributions = dict(zip(github_usernames, contributions))
        ranking = sorted(contributions.items(), key=lambda x: x[1], reverse=True)

        global global_ranking
        global_ranking = [
            {"username": entry[0], "contributions": entry[1]} for entry in ranking
        ]


@app.route("/")
def scrape_and_deliver():
    try:
        f = open("usernames.txt", "r")
        github_usernames = [line.strip() for line in f.readlines()]
        f.close()
    except FileNotFoundError:
        github_usernames = os.environ.get("github_usernames")
        if not github_usernames:
            return make_response({"details": "usernames not found"})
        else:
            github_usernames = github_usernames.split(",")

    if ASYNC:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async(github_usernames))
    else:
        main_sync(github_usernames)

    global global_ranking
    return make_response({"results": global_ranking})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
