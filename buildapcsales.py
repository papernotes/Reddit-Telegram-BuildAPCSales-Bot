"""
    Telegram bot that notifies when GPUs are < $120
"""
import praw
import time
import re
import herokuDB
import telebot      # Telegram wrapper
import tgTOKEN      # contains TOKEN
from sqlalchemy import create_engine
from sqlalchemy import text

REDDIT_CLIENT = praw.Reddit(user_agent="Searches /r/buildapcsales for sales")
REDDIT_CLIENT.login(disable_warning=True)

CACHE = []          # contains posts we searched
PHRASES = ['gpu']   # list of phrases for items we want

# create the telegram bot
tg_bot = telebot.TeleBot(tgTOKEN.TOKEN)
users_list = []     # list of users to send message to

# create the ENGINE for the database
#ENGINE = create_engine(herokuDB.url)


def run_bot():
    global CACHE
    global PHRASES
    """
        Main driver of the bot
    """

    '''
    result = ENGINE.execute("select * from searched_posts")

    # set up the cache for usage
    for row in result:
        TEMP_CACHE.append(str(row[0]))

    for value in TEMP_CACHE:
        if value not in CACHE:
            CACHE.append(str(value))
    '''

    # set up the buildapcsales subreddit
    subreddit = REDDIT_CLIENT.get_subreddit("buildapcsales")

    # search through the hot submissions
    print ("Searching through hot submissions")
    for submission in subreddit.get_hot(limit=100):
        determine_value(submission)


    # search through the new submissions
    print ("Searching through new submissions")
    for submission in subreddit.get_new(limit=100):
        determine_value(submission)


def is_under_threshold(submissionTitle):
    """
        Determines if the price is under the threshold
    """

    top_price = 0

    # find the prices in the title
    prices = re.findall(r'\$(\d+)', submissionTitle)

    # convert values of the prices to int
    prices = [int(value) for value in prices]

    for price in prices:
        if price > top_price:
            top_price = price

        if 100 < top_price and top_price < 150:
            return True


def calculate_score(submission):
    """
        Calculates teh score perecentage of the submission
        Returns 0 if the submission's score is 0
    """
    # get the submission's upvote ratio
    ratio = REDDIT_CLIENT.get_submission(submission.permalink).upvote_ratio

    # if the submission's score is 0, ignore it
    if (submission.score == 0):
        return 0

    # if the submission's score isn't 0, continue
    else:
        # the value of the post is this
        calcUps = round((ratio * submission.score) / (2 * ratio - 1))

        # if the result of the above calculation is 0, return 0
        if (calcUps == 0):
            return 0

        # assign value to the calculated value and return that
        else:
            global value
            value = round(submission.ups / calcUps * 100, 2)
            return value


def determine_value(submission):
    """
        Determines if the submission is worth looking at
    """
    post_title = submission.title.lower()

    if (any(string in post_title for string in PHRASES) and
        submission.id not in CACHE):

        # Deal under $120 and well-received
        if is_under_threshold(post_title) and calculate_score(submission) >= 85:
            print ("\nDeal found under threshold with a good score!")
            print ("Score is " + str(calculate_score(submission)))
            print submission.title
            send_message(submission, 1)

        # Deal only under $120
        elif is_under_threshold(post_title) and not calculate_score(submission) >= 85:
            print ("\nDeal found under threshold")
            print submission.title
            send_message(submission, 2)

        # Deal only well-received
        elif not is_under_threshold(post_title) and calculate_score(submission) >= 85:
            print ("\nFound a well-received deal!")
            print ("Score is " + str(calculate_score(submission)))
            print submission.title
            CACHE.append(submission.id)
            send_message(submission, 3)

        else:
            CACHE.append(submission.id)


def send_message(submission, deal_type):
    for users in users_list:

        # Deal under threshold and has good score
        if deal_type == 1:
            tg_bot.send_message(users, "Deal found under threshold with " +
                                "a good score!" + "\n\nScore is " +
                                str(calculate_score(submission)) +
                                "\n\nTitle: " + str(submission.title) +
                                "\nLink: " + str(submission.short_link))

        # Under threshold deal
        elif deal_type == 2:
            tg_bot.send_message(users, "Deal found under threshold!" +
                                "\n\nTitle: " + str(submission.title) +
                                "\nLink: " + str(submission.short_link))

        # Well-received deal
        else:
            tg_bot.send_message(users, "Found a well-received deal!" +
                                "\n\nScore is " + 
                                str(calculate_score(submission)) +
                                "\n\nTitle: " + str(submission.title) +
                                "\nLink: " + str(submission.short_link))

        CACHE.append(submission.id)



@tg_bot.message_handler(commands=['start'])
def welcome(message):
    tg_bot.reply_to(message, "Hello! You've been added to BuildAPCSalesBot's"+
                 " recpients! Type '/end' to stop messages from this bot.")

    # Add the user to the list of recipients
    users_list.append(message.chat.id)
    print (str(message.chat.id) + " Added")


@tg_bot.message_handler(commands=['end'])
def remove(message):
    bot.reply_to(message, "You've been removed from the list of recipients!\n"+
                 "Type '/start/ to re-add yourself to the list again.")

    # remove user from the list
    users_list.remove(message.chat.id)
    print (str(message.chat.id) + " Removed")





# Database
def write_to_file(sub_id):
    """
        Save the submissions we searched
    """
    if not id_added(sub_id):
        temp_text = text('insert into searched_posts (post_id) values(:postID)')
        ENGINE.execute(temp_text, postID=sub_id)


def id_added(sub_id):
    """
        Check to see if the item is already in the database
    """

    is_added_text = text("select * from searched_posts where post_id = :postID")
    if (ENGINE.execute(is_added_text, postID=sub_id).rowcount != 0):
        return True
    else:
        return False


def clear_column():
    """
        Clear our column/database if our rowcount is too high
    """

    num_rows = ENGINE.execute("select * from searched_posts")
    if (num_rows.rowcount > 2000):
        ENGINE.execute("delete from searched_posts")
        print("Cleared database")


print ("Bot started")

try:
    tg_bot.polling()
except Exception:
    pass

run_bot()

# TODO 
''' For later      Create a counter for the clearing of the column
while True:
    try:
        time.sleep(10)
        for users in users_list:
            bot.send_message(users, "Test")
    except:
        break
    # run the bot continuously
    run_bot()

    # reset the cache
    TEMP_CACHE = []

    print ("Sleeping")
    time.sleep(300)
'''


