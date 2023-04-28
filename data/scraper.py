import praw
import tqdm

def clean_text(text: str) -> str: #Strip text
    return text.strip()

def scrape_subreddit(reddit: praw.Reddit, data: list, subreddit: str, max_allow_len: int = 512) -> int:
    print("Scraping", subreddit)
    hot_posts = reddit.subreddit(subreddit).hot(limit = 10000)
    maxlen = -1
    for post in tqdm.tqdm(hot_posts):
        if post.stickied or post.pinned: # Skip headers
            continue
        question = ""
        if post.title[-1] not in [".", "!", "?"]:
            question += clean_text(post.title) + "."
        else:
            question += clean_text(post.title)

        if len(list(bytes(post.selftext, "utf8"))) < max_allow_len//2:
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
                    if len(data[-1]) > maxlen:
                        maxlen = len(data[-1])
                continue

            if top_level_comment.body == "[removed]" or top_level_comment.stickied:
                continue
            res = question + clean_text(top_level_comment.body) + "\0"
            if len(list(bytes(res, "utf8"))) > max_allow_len:
                continue
            data.append(res)
            
            if len(data[-1]) > maxlen:
                maxlen = len(data[-1])

    return maxlen

reddit = praw.Reddit(client_id="fO05Zgvq53-yoAPrz-Yesw", client_secret='9rkeMCecw-qDgRrfWUQAuJ-yUoz6LQ', user_agent='Web Scraper')

data = []
maxlen = -1

subreddits = [
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
    "AskHistorians", #v2
    "explainlikeimfive",
    "cscareerquestions", #v3
    "questions",
    "rust",
    "C_programming", #v4
    "pythonhelp",
    "math",
    "AskScienceDiscussion",
]

for i, subreddit in enumerate(subreddits):
    print(f"{i+1}/{len(subreddits)}")
    try:
        max = scrape_subreddit(reddit, data, subreddit) 
        if max > maxlen:
            maxlen = max

        print(len(data))
    except Exception as e:
        print(e)

try:
    print(len(data),"data points")
    print("Max length:",maxlen)
    print("Average length:", sum([len(item) for item in data])/len(data))
except Exception as e:
    print(e)

with open("reddit_scrape_v4.txt", "w") as f:
    f.write("\n".join(data))