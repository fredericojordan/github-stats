import asyncio

from timeit import default_timer

import aiohttp
import requests
from bs4 import BeautifulSoup


def parse_contribuition_count(html_page):
    return int(
        BeautifulSoup(html_page, "html.parser")
        .find("div", {"class": "js-yearly-contributions"})
        .text.strip()
        .split()[0]
        .replace(",", "")
    )


def get_contributions_page_sync(github_tag):
    url = f"https://github.com/users/{github_tag}/contributions"
    response = requests.get(url)
    return response.content


def get_contribution_count_sync(github_tag):
    html_page = get_contributions_page_sync(github_tag)
    return parse_contribuition_count(html_page)


def main_sync(github_tags):
    contributions = {
        github_tag: {"contributions": get_contribution_count_sync(github_tag)}
        for github_tag in github_tags
    }
    ranking = sorted(
        contributions.items(), key=lambda x: x[1]["contributions"], reverse=True
    )
    for i, c in enumerate(ranking):
        print(f"{i+1}. ({c[1]['contributions']}) {c[0]}")


async def get_contributions_page_async(session, github_tag):
    url = f"https://github.com/users/{github_tag}/contributions"
    async with session.get(url) as response:
        return await response.text()


async def main_async(github_tags):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for tag in github_tags:
            tasks.append(get_contributions_page_async(session, tag))
        profile_pages = await asyncio.gather(*tasks)

        contributions = [
            parse_contribuition_count(html_page) for html_page in profile_pages
        ]
        contributions = dict(zip(github_tags, contributions))
        ranking = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        for i, c in enumerate(ranking):
            print(f"{i + 1}. ({c[1]}) {c[0]}")


if __name__ == "__main__":
    # if ASYNC:
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(main_async(GITHUB_TAGS))
    # else:
    #     main_sync(GITHUB_TAGS)

    try:
        f = open("tags.txt", "r")
        github_tags = [line.strip() for line in f.readlines()]
        f.close()
    except FileNotFoundError:
        print("File 'tags.txt' not found.")
        exit(-1)

    # Async
    print(f"\n\nFetching async...")
    async_start = default_timer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async(github_tags))
    async_end = default_timer()
    print(f"Time async: {async_end - async_start}")

    # Sync
    print(f"\n\nFetching sync...")
    sync_start = default_timer()
    main_sync(github_tags)
    sync_end = default_timer()
    print(f"Time sync: {sync_end - sync_start}")
