import praw
import time

# from file import function

# being praw and log in
r = praw.Reddit(user_agent = "Searching for Deals in /r/buildapcsales")
r.login(disable_warning=True)



# the number of times searched
searches = 0
cache = []

print ("")
print ("Bot Search Started")
print ("")


# run_bot looks through submissions and finds matching posts
def run_bot():
	# so that "searches" is global and can be reached anywhere
	global searches

	# enter /r/buildapcsales subreddit
	subreddit = r.get_subreddit("buildapcsales")

	# open up the searched posts that have been saved before
	with open("searched_posts.txt") as searched_posts:
		# set the cache to be the lines of the post
		cache = searched_posts.readlines()
		# strip newlines so we can determine if we searched post already
		cache = [line.strip('\n') for line in cache]


	# for the subreddit, get the new posts
	for submission in subreddit.get_hot(limit = 10):

		print ("Searching...")
		print ("Submissions searched so far: " + str(searches))

	
		# set hasDeal to whether or not the post has matching phrases
		# TODO		hasDeal = any(string in post_title for string in phrases)


		#if submission.id not in cache of text file
		if submission.id not in cache:

			# if the score of the submission is greater than 90% (worth)
			if (calculateScore(submission) >= 85):

				# determine the value of the submission
				printStats(submission)
				storeStats(submission)

				# append to the file the submission id
				with open("searched_posts.txt", "a") as searched_posts:
					searched_posts.write(submission.id)
					searched_posts.write('\n')

			# ignore the not as valuable posts
			else:
				# append to the file the submission id
				with open("searched_posts.txt", "a") as searched_posts:
					searched_posts.write(submission.id)
					searched_posts.write('\n')

		# increment the number of submissions searched
		searches = searches+1

	print ("end loop")


# gets only the name of the item based on the [ITEM]NAME(PRICE) format
def get_itemName(title):
	# the position of the ']' in the title post
	try:
		title = title.split(']')[1]
		title = title.split('(')[0]
		return title
	except:
		return "Item Name Unobtainable"




# calcuates the score percentage of the submission
# returns 0% if the submission's score is 0
def calculateScore(submission):
	# get the submission's upvote ratio
	ratio = r.get_submission(submission.permalink).upvote_ratio

	# if the submission's score is 0, ignore it
	if (submission.score == 0):
		return 0

	# if the submission's score isn't 0, continue
	else:
		# the value of the post is this
		calcUps = round((ratio*submission.score)/(2*ratio - 1))

		# if the result of the above calculation is 0, return 0
		if (calcUps == 0):
			return 0

		# assign value to the calculated value and return that
		else:
			global value
			value = round(submission.ups/calcUps*100, 2)
			return value




# prints out the deal's information to terminal
def printStats(submission):
	# sets the post's title to lowercase
	post_title = submission.title.lower()

	print ("	DEAL INFORMATION: ")
	print ("Post Title = " + post_title)	# print the name of the post
	print ("Item Name = " + get_itemName(post_title))	# get the item name in the post
	print ("Number of Comments = " + str(submission.num_comments))	# display the nubmer of comments
	print ("Number of Upvotes = " + str(submission.ups))
	print ("Submission ID = " + str(submission.id))
	print ("Calculated Percent Upvotes = " + str(value) + "%")
	print ("Reddit Link = " + submission.short_link)	# get the shortened link of the post
	print ("Shared Link = " + submission.url)
	print ("")


# stores the statistics of the item to a text file
def storeStats(submission):
	# sets the post's title to lowercase
	post_title = submission.title.lower()

	with open("savedStats.txt", "a") as savedStats:
		savedStats.write("	Post Title = " + post_title + "\n")
		savedStats.write("	Item Name = " + get_itemName(post_title) + "\n")
		savedStats.write("	Calculated Percent Upvotes = " + str(value) + "%\n")
		savedStats.write("	Reddit Link = " + submission.short_link + "\n")
		savedStats.write("	Shared Link = " + submission.url + "\n")
		savedStats.write("\n")



# running the bot continuously
while True:
	# run the bot
	run_bot()

	# clear the cache
	#open("searched_posts.txt", "w").close()

	# rest for 10 seconds
	time.sleep(10)


