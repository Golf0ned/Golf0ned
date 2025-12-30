import os
import requests

graphql_url = "https://api.github.com/graphql"


def generate_readme(username: str, token: str, path: str = "README.md"):
    languages = get_languages(username, token).items()

    total_size = sum(size for _, size in languages)
    with open(path, "w", encoding="utf-8") as readme:
        readme.write("## Top Languages\n")
        readme.write("```\n")
        for lang, size in list(languages)[:10]:
            percent = (size / total_size) * 100 if total_size > 0 else 0
            bar = percent_bar(percent)
            readme.write(f"{lang:<12} {bar} {percent:.2f}%\n")
        readme.write("```\n")


def get_languages(username: str, token: str):
    query = """
    query userInfo($login: String!) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
          nodes {
            name
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  color
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }

    payload = {"query": query, "variables": {"login": username}}

    response = requests.post(graphql_url, json=payload, headers=headers)
    response.raise_for_status()

    res = response.json()
    repo_nodes = res["data"]["user"]["repositories"]["nodes"]

    languages = {}
    for repo in repo_nodes:
        edges = repo["languages"]["edges"]
        if not edges:
            continue

        for edge in edges:
            lang_name = edge["node"]["name"]
            lang_size = edge["size"]

            languages[lang_name] = languages.get(lang_name, 0) + lang_size

    sorted_languages = dict(
        sorted(
            languages.items(),
            key=lambda pair: pair[1],
            reverse=True,
        )
    )

    return sorted_languages


def percent_bar(percent: float, width: int = 20):
    percent = max(0, min(100, percent))
    filled = round((percent / 100) * width)
    empty = width - filled

    return f"[{'█' * filled}{'░' * empty}]"


if __name__ == "__main__":
    username = "golf0ned"
    token = os.getenv("GITHUB_TOKEN", "")

    generate_readme(username, token)
