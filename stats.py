import asyncio
import logging
import os

import aiohttp

LOGGER = logging.getLogger(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    LOGGER.error("Please set GITHUB_TOKEN environment variable")
    exit(-1)


class MergeableDict(dict):
    def __or__(self, o):
        self.update(o)
        return self


async def async_api_info(session, github_username):
    url = "https://api.github.com/graphql"
    query_body = 'query {{ user(login: "{username}") {{ name avatarUrl(size:80) contributionsCollection {{ contributionCalendar {{ totalContributions }} }} }} }}'.format(
        username=github_username
    )
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    async with session.post(
        url, json={"query": query_body}, headers=headers
    ) as response:
        return await response.json()


async def get_profile_data(session, github_username):
    profile_data = await async_api_info(session, github_username)

    try:
        return MergeableDict(
            {
                "username": github_username,
                "contributions": profile_data["data"]["user"]["contributionsCollection"][
                    "contributionCalendar"
                ]["totalContributions"],
                "avatar": profile_data["data"]["user"]["avatarUrl"],
            }
        )
    except Exception:
        return MergeableDict({"username": github_username, "contributions": -1})


async def rank_profiles(github_usernames):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for username in github_usernames:
            tasks.append(get_profile_data(session, username))
        profiles = await asyncio.gather(*tasks)

    sorted_rank = sorted(profiles, key=lambda x: x["contributions"], reverse=True)
    return [v | {"position": i + 1} for i, v in enumerate(sorted_rank)]


def scrape():
    try:
        f = open("usernames.txt", "r")
        github_usernames = [line.strip() for line in f.readlines()]
        f.close()
    except FileNotFoundError:
        github_usernames = os.environ.get("GITHUB_USERNAMES")
        if not github_usernames:
            LOGGER.error("usernames not found")
            return
        else:
            github_usernames = github_usernames.split(",")

    loop = asyncio.get_event_loop()
    ranking = loop.run_until_complete(rank_profiles(github_usernames))

    return {"results": ranking}


if __name__ == "__main__":
    response = scrape()
    if response:
        for r in response["results"]:
            print(f"{r['position']}. ({r['contributions']}) {r['username']}")
