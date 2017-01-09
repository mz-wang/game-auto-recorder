import argparse
import logging
import sys
import os
import errno
import requests
import time

from selenium import webdriver

FORMAT = "%(asctime)-15s - %(levelname)s - %(module)20s:%(lineno)-5d - %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
LOG = logging.getLogger(__name__)

RESOURCES_PATH = os.path.join(os.getcwd(), "resources")
ERRORS_PATH = os.path.join(os.getcwd(), "errors")
FIND_SUMMONER_BY_NAME_URL = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}"
GET_CURRENT_GAME_URL = "https://na.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/NA1/{}?api_key={}"
OPGG_URL = "http://na.op.gg/summoner/userName={}"
WAIT_FOR_OPGG_MAX_SECONDS = 12


def read_summoner_names(file_name):
    file_path = os.path.join(RESOURCES_PATH, file_name)
    if not os.path.exists(file_path):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
    with open(file_path, 'r') as f:
        return [name.strip('\n') for name in f]


def check_rate_limit_exceeded(code):
    if code is 429:
        raise RuntimeError("rate limit exceeded")


def get_player_id(ign, key):
    r = requests.get(FIND_SUMMONER_BY_NAME_URL.format(ign, key))
    check_rate_limit_exceeded(r.status_code)
    if r.status_code is not 200:
        raise RuntimeError("error finding summoner: {}".format(ign))
    return r.json()[ign]["id"]


def is_player_in_game(ign, key):
    player_id = get_player_id(ign, key)
    r = requests.get(GET_CURRENT_GAME_URL.format(player_id, key))
    check_rate_limit_exceeded(r.status_code)
    if r.status_code is 200:
        LOG.info("game found for: {}".format(ign))
        return True
    return False


def element_exists(driver, xpath):
    try:
        element = driver.find_element_by_xpath(xpath)
    except Exception:
        return None
    return element


def click_find_game_and_record(ign):
    driver = webdriver.PhantomJS(executable_path=os.path.join(RESOURCES_PATH, "phantomjs"))
    try:
        driver.get(OPGG_URL.format(ign))
        driver.find_element_by_id("SpectateButton").click()

        start = time.time()
        end = time.time()
        e = element_exists(driver, "//div[@class='Recording']/a")
        while e is None and end - start < WAIT_FOR_OPGG_MAX_SECONDS:
            e = element_exists(driver, "//div[@class='Recording']/a")
            end = time.time()

        if element_exists(driver, "//div[@class='Recording']/div[contains(@class, 'NowRecording')]") is not None:
            LOG.info("already recording for: {}".format(ign))
            return

        e.click()
        LOG.info("started recording for: {}".format(ign))
    except Exception:
        LOG.error("could not record: {}".format(ign))
        if not os.path.exists(ERRORS_PATH):
            os.makedirs(ERRORS_PATH)
        driver.save_screenshot(os.path.join(ERRORS_PATH, "ss_{}_{}.png".format(ign, time.time())))
    driver.close()


def parse_args():
    parser = argparse.ArgumentParser(description='check players and record through op.gg if in-game')
    parser.add_argument('-p', '--players', type=str, help='name of file containing newline separate list of IGNs')
    parser.add_argument('-k', '--api-key', type=str, help='Riot Games API Key')
    args = parser.parse_args()
    return args


def main(args):
    igns = read_summoner_names(args.players)
    LOG.info("running recorder.py for {}".format(igns))
    for ign in igns:
        ign = ign.replace(" ", "")
        if is_player_in_game(ign, args.api_key):
            click_find_game_and_record(ign)


if __name__ == "__main__":
    main(parse_args())
