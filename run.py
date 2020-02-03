import multiprocessing as mp
from random import choice
from threading import Thread
from time import strftime, sleep

from instabot import Bot


class Start():
    def __init__(self, username, password):
        self.user_name = username
        self.pass_word = password
        self.max_follows_per_day = 750
        self.bot = Bot(
            followed_file='followed/%s_followed.txt' % (username),
            whitelist_file='whitelist/%s_whitelist.txt' % (username),
            unfollowed_file='unfollowed/%s_unfollowed.txt' % (username),
            skipped_file='skipped/%s_skipped.txt' % (username),
            max_follows_per_day=self.max_follows_per_day,
            max_unfollows_per_day=self.max_follows_per_day,
            max_likes_per_day=self.max_follows_per_day / 2,
            follow_delay=100,
            unfollow_delay=100,
            like_delay=500,
            comment_delay=350)
        self.hashtag_file = self.bot.read_list_from_file('hashtag.txt')
        self.recommendations = False
        self.users_file = self.bot.read_list_from_file('user.txt')
        loggedIn = self.log_in()
        if not loggedIn:
            raise Exception('Wrong credentials - please check your username and password')
        self.run_bot_process()
        while True:
            sleep(3600)

    def run_bot_process(self):
        self.run(self.stats)
        self.run(self.followUsersFollowers)
        self.run(self.likeHashtagMedias)
        self.run(self.unfollow_everyday)

    def log_in(self):
        return self.bot.login(username=self.user_name, password=self.pass_word,
                       cookie_fname='cookie/%s_cookie.txt' % (self.user_name), use_cookie=False)


    @staticmethod
    def run(job_fn):
        job_thread = Thread(target=job_fn)
        job_thread.start()

    def stats(self):
        while True:
            self.bot.save_user_stats(self.user_name, path='stats/')
            sleep(6 * 60 * 60)
            self.sleepDuringNight()

    def followUsersFollowers(self):
        thereIsNoError = True
        while thereIsNoError:
            self.sleepDuringNight()
            try:
                usersList = self.getRandomUserFollowers()
                for user in usersList:
                    self.bot.follow(user_id=user)
            except Exception as exception:
                print(exception)
                sleep(3600)

    def likeHashtagMedias(self):
        thereIsNoError = True
        numberOfTimesFailed = 0
        while thereIsNoError:
            self.sleepDuringNight()
            try:
                hashtag = choice(self.hashtag_file)
                hashtagMedias = self.bot.get_hashtag_medias(hashtag)
                self.likeMedias(hashtagMedias)
            except Exception as exception:
                sleep(3600)
                print(exception)
                numberOfTimesFailed = numberOfTimesFailed + 1
                if numberOfTimesFailed >= 5:
                    break

    def likeMedias(self, hashtagMedias):
        for media in hashtagMedias:
            self.bot.like(media, check_media=False)

    def getRandomUserFollowers(self):
        randomUser = choice(self.users_file)
        if self.recommendations:
            userFollowers = self.bot.get_user_followers(
                user_id=randomUser, nfollows=1000)
        else:
            userFollowers = self.bot.get_user_followers(
                user_id=randomUser, nfollows=60)
        return userFollowers

    def sleepDuringNight(self):
        currentHour = int(strftime("%H"))
        print(currentHour)
        sleepFrom = 1
        sleepUntil = 5
        if sleepFrom <= currentHour <= sleepUntil:
            sleepTimeInHours = 0
            if currentHour > sleepFrom:
                sleepTimeInHours = currentHour - sleepFrom
            else:
                sleepTimeInHours = sleepUntil - currentHour
            sleepTimeInSeconds = sleepTimeInHours * 3600
            print('sleeping for %s seconds' % (sleepTimeInSeconds))
            sleep(sleepTimeInSeconds)
        else:
            print('time for sleeping have not yet been met')

    def unfollow_everyday(self):
        while True:
            self.bot.unfollow_everyone()
            sleep(3600 * 10)


if __name__ == '__main__':
    mp.get_context('spawn')
    q = mp.Queue()

    print('input username: ')
    username = input()
    print('input password: ')
    password = input()
    mp.Process(target=Start, args=([username, password])).start()
