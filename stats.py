import asyncio
import os

import aiohttp
from bs4 import BeautifulSoup
from flask import make_response


class MergeableDict(dict):
    def __or__(self, o):
        self.update(o)
        return self


def parse_contribuition_count(html_page):
    return int(
        BeautifulSoup(html_page, "html.parser")
        .find("div", {"class": "js-yearly-contributions"})
        .text.strip()
        .split()[0]
        .replace(",", "")
    )


async def async_get_contributions_page(session, github_username):
    url = f"https://github.com/users/{github_username}/contributions"
    async with session.get(url) as response:
        html_page = await response.text()
        return parse_contribuition_count(html_page)


async def async_get_avatar(session, github_username):
    url = f"https://github.com/{github_username}.png"
    async with session.get(url) as response:
        await response.read()
        return str(response.url)


async def get_profile_data(session, github_username):
    contributions = await async_get_contributions_page(session, github_username)
    avatar = await async_get_avatar(session, github_username)
    return MergeableDict({
        "username": github_username,
        "contributions": contributions,
        "avatar": avatar + "&s=80",
    })


async def rank_profiles(github_usernames):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for username in github_usernames:
            tasks.append(get_profile_data(session, username))
        profiles = await asyncio.gather(*tasks)

    sorted_rank = sorted(profiles, key=lambda x: x["contributions"], reverse=True)
    return [v | {"position": i+1} for i, v in enumerate(sorted_rank)]


def scrape():
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

    loop = asyncio.get_event_loop()
    ranking = loop.run_until_complete(rank_profiles(github_usernames))

    return {"results": ranking}
