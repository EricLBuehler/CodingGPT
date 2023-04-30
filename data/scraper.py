import praw
import tqdm
import shutil
import re

class TargetReached(Exception):
    pass

class Done(Exception):
    pass

# Validate URL
url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
url_extract_pattern = "[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"

def clean_text(text: str) -> str: #Strip text
    return text.strip()

def scrape_subreddit(reddit: praw.Reddit, data: list, subreddit: str, target: int, prev_len: int, max_allow_len: int = 512, allow_selftext: bool = True) -> int:
    print("Scraping", subreddit)
    hot_posts = reddit.subreddit(subreddit).hot(limit = 10000)
    maxlen = -1
    for post in tqdm.tqdm(hot_posts):
        if post.stickied or post.pinned: # Skip headers
            continue
        question = ""
        if clean_text(post.title)[-1] not in [".", "!", "?"]:
            question += clean_text(post.title) + "."
        else:
            question += clean_text(post.title)

        if allow_selftext:
            is_below_half_maxlen = 0 < len(list(bytes(post.selftext, "utf8"))) < max_allow_len//2
            is_http_url = re.match(url_pattern, clean_text(post.selftext)) is not None
            is_no_http_url = re.match(url_extract_pattern, clean_text(post.selftext))
            if len(clean_text(post.selftext))>0:
                is_same_as_title_punctuated = clean_text(post.selftext)[-1] in [".", "!", "?"] and clean_text(post.selftext)[:-1] != question
                is_same_as_title_nonpunctuated = clean_text(post.selftext)[-1] not in [".", "!", "?"] and clean_text(post.selftext)[:-1]+"." != question
            
            if is_below_half_maxlen and (is_http_url or is_no_http_url):
                if is_same_as_title_punctuated or (len(clean_text(post.selftext))>0 and is_same_as_title_nonpunctuated):
                    question += " "
                    question += clean_text(post.selftext)

        question += "\n"

        for top_level_comment in reddit.submission(id=post.id).comments:
            if isinstance(top_level_comment, praw.models.MoreComments):
                for comment in top_level_comment.comments():
                    if not hasattr(comment, "body"):
                        continue
                    if comment.body == "[removed]" or comment.stickied:
                        continue
                    res = question + clean_text(comment.body) + "\0"
                    if len(list(bytes(res, "utf8"))) > max_allow_len:
                        continue
                    data.append(res)
                    if len(data)+prev_len == target:
                        raise TargetReached()
                    if len(data[-1]) > maxlen:
                        maxlen = len(data[-1])
                continue

            if top_level_comment.body == "[removed]" or top_level_comment.stickied:
                continue
            res = question + clean_text(top_level_comment.body) + "\0"
            if len(list(bytes(res, "utf8"))) > max_allow_len:
                continue
            data.append(res)
            if len(data)+prev_len == target:
                raise TargetReached()
            if len(data[-1]) > maxlen:
                maxlen = len(data[-1])

    return maxlen

reddit = praw.Reddit(client_id="fO05Zgvq53-yoAPrz-Yesw", client_secret='9rkeMCecw-qDgRrfWUQAuJ-yUoz6LQ', user_agent='Web Scraper')

reddit.config.timeout = (4 * 3600) #4 hours

data = []
output = data
maxlen = -1

subreddits_v1 = [
    "AskScience",
    "LearnProgramming",
    "LearnPython",
    "cpp_questions",
    "javahelp",
    "askprogramming",
    "java",
    "CodingHelp",
    "AskProgrammers",
    "datascience",
    "flask",
    "AskStatistics",
]
subreddits_v2 = [
    "AskHistorians", #v2
    "explainlikeimfive",
]
subreddits_v3 = [
    "cscareerquestions", #v3
    "questions",
    "rust",
]
subreddits_v4 = [
    "C_programming", #v4
    "pythonhelp",
    "math",
    "AskScienceDiscussion",
]
subreddits_v5 = [
    "mathematics", #v5
    "science",
    "webdev",
    "github",
    "creativecoding",
    "arduino",
    "javascript",
    "IWantToLearn",
]
subreddits_v6 = [
    "program", #v6
    "ProgrammingPrompts",
    "linux_programming",
    "haskell",
    "backendProgramming",
    "EverythingScience",
    "computerscience",
    "AskComputerScience",
    "PythonPandas",
    "pythoncoding",
    "madeinpython",
    "coolgithubprojects",
    "learnmachinelearning",
    "raspberry_pi",
] 
subreddits_v7 = [
    "learnjavascript", #v7
    "JavaScriptTips",
    "cpp",
    "cprogramming",
    "csharp",
    "gamedev",
    "swift",
    "Cplusplus",
    "learncsharp",
    "gcc",
    "julia",
    "programminghelp",
    "learnc",
    "learnjava",
    "functionalprogramming"
    "HomeworkHelp",

]

version = 7
target = 100_000

prev_len = 0

if version > 1:
    shutil.copyfile(f"reddit_scrape_v{version-1}.txt", f"reddit_scrape_v{version}.txt")
    with open(f"reddit_scrape_v{version-1}.txt", "r") as f:
        prev_len = len(f.read().split("\0"))
        print(f"{prev_len=}")

subreddit_name = f"subreddits_v{version}"

for i, subreddit in enumerate(locals()[subreddit_name]):
    print(f"{i+1}/{len(locals()[subreddit_name])}")
    try:
        max = scrape_subreddit(reddit, data, subreddit, target, prev_len, allow_selftext=True) 
        if max > maxlen:
            maxlen = max

        print(len(data))
    except TargetReached:
        print(f"Target of {target} reached.")
        data = [] #output will stay as old data
            
    except KeyboardInterrupt:
        while True:
            cont = input("Do you want to continue? (y/n) ")
            if cont.lower().strip() == "y":
                break
            else:
                raise Done()
    except Exception as e:
        print(e)
 
try:
    print(len(output),"data points")
    print("Max length:",maxlen)
    print("Average length:", sum([len(item) for item in output])/len(output))
except Exception as e:
    print(e)

with open(f"reddit_scrape_v{version}.txt", "a+") as f:
    f.write("\n".join(output))

if output is not data:
    print(len(data),"overflow data points")
    with open(f"overflow_v{version}.txt", "a+") as f:
        f.write("\n".join(data))