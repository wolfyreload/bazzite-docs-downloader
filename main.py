import time
import requests
import re


processed = set()
url_set = {'https://universal-blue.discourse.group/docs?topic=561'}
url_pattern = re.compile(r'(https://universal-blue.discourse.group/docs\?topic=\d+)')
topic_pattern = re.compile(r'(https://universal-blue.discourse.group/docs\?topic=(\d+))')


def strip_comments(text: str):
    index_first_comment = text.index("-------------------------")
    index_first_newline = text.index("\n")
    text_body = text[index_first_newline:index_first_comment]
    return text_body.strip()


def get_url_links(text: str):
    url_list = re.findall(url_pattern, text)
    return url_list


def get_markdown_from_url(documentation_url: str) -> str | None:
    while True:
        documentation_url = documentation_url.replace("docs?topic=", "raw/")
        response = requests.get(documentation_url, timeout=2)
        if response.status_code == 403:
            print(f"{response.status_code} {documentation_url}")
            return None
        elif response.status_code != 200:
            print(f"{response.status_code} {documentation_url}")
            time.sleep(1)
        else:
            markdown = response.text
            return markdown


def convert_to_local_links(text: str):
    return re.sub(topic_pattern, lambda match: f"{match.group(2)}.md", text)


def write_markdown_file(markdown_text, file_name):
    with open(f"md/{file_name}", "w") as f:
        print(f"md/{file_name}")
        f.write(markdown_text)


if __name__ == '__main__':
    while True:
        if len(url_set) == 0:
            break

        url = url_set.pop()
        file_name = url.split("=")[-1]+".md"

        if file_name in processed:
            continue

        markdown_text = get_markdown_from_url(url)

        if markdown_text is None:
            continue

        markdown_text = strip_comments(markdown_text)
        url_links = get_url_links(markdown_text)
        markdown_text = convert_to_local_links(markdown_text)
        url_set = url_set.union(url_links)
        write_markdown_file(markdown_text, file_name)
        processed.add(file_name)

