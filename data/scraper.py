import praw
import tqdm

def clean_text(text: str) -> str: #Strip text
    return text.strip()

def scrape_subreddit(reddit: praw.Reddit, data: list, subreddit: str, max_allow_len: int = 1024) -> int:
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

        if len(list(bytes(post.selftext, "utf8"))) < 512:
            question += " "
            question += clean_text(post.selftext)
        question += "\n"
        
        for top_level_comment in reddit.submission(id=post.id).comments:
            if isinstance(top_level_comment, praw.models.MoreComments):
                for comment in top_level_comment.comments():
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

try:
    max = scrape_subreddit(reddit, data, "AskScience") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "LearnProgramming") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "LearnPython") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "cpp_questions") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "javahelp") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "askprogramming") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "java") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "CodingHelp") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "AskProgrammers") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "datascience") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "flask") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    max = scrape_subreddit(reddit, data, "AskStatistics") 
    if max > maxlen:
        maxlen = max
except:
    pass

try:
    print(len(data),"data points")
    print("Max length:",maxlen)
    print("Average length:", sum([len(item) for item in data])/len(data))
except:
    pass

with open("reddit_scrape.txt", "w") as f:
    f.write("\n".join(data))