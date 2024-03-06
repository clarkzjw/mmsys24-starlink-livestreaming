from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium import webdriver
from plot import generate_plots
from selenium.common import exceptions
import logging
from config import URL, Experiment
import urllib.parse
from multiprocessing import Process
from tc import tc_thread
import requests


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


logger = logging.getLogger("runner")


def run_once(EXPERIMENT_ID: str, exp: Experiment) -> None:
    logger.info("running {}".format(EXPERIMENT_ID))

    options = webdriver.ChromeOptions() 
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    # options.add_argument("--headless")
    options.add_argument('ignore-certificate-errors')

    # FIXME: change to wait-for-it to detect whether remote chrome is alive
    logger.info("wait 10 seconds before connecting to remote chrome")
    time.sleep(10)

    try:
        logger.info("connecting to remote chrome instance")
        driver = webdriver.Remote("http://chrome:4444", options=options)
        logger.info("remote chrome instance connected")

        driver.maximize_window()

        params = {
            "experimentID": EXPERIMENT_ID,
            "mpdURL": exp.MPD_URL,
            "targetLatency": exp.TARGET_LATENCY,
            "constantVideoBitrate": exp.CONSTANT_VIDEO_BITRATE,
            "abrGeneral": exp.ABR_ALGORITHM,
            "maxDrift": exp.MAX_DRIFT,
            "minCatchupPlaybackRate": exp.MIN_CATCHUP_PLAYBACK_RATE,
            "maxCatchupPlaybackRate": exp.MAX_CATCHUP_PLAYBACK_RATE,
            "abrAdditionalAbandonRequestRule": "true",
            "cmabAlpha": exp.CMAB_ALPHA,
        }
        if exp.ABR_ALGORITHM == "abrLoLP":
            params["catchupMechanism"] = "liveCatchupModeLoLP"
        elif exp.ABR_ALGORITHM == "abrCMAB":
            params["catchupMechanism"] = "liveCatchupModeCMAB"
        else:
            params["catchupMechanism"] = "liveCatchupModeDefault"

        # if CATCH_UP is specified in experiment.json
        # it overrides the catchupMechanism
        if exp.CATCH_UP in ["liveCatchupModeLoLP", "liveCatchupModeCMAB", "liveCatchupModeDefault"]:
            params["catchupMechanism"] = exp.CATCH_UP

        url = URL + urllib.parse.urlencode(params)
        logger.info(url)

        driver.get(url)

        logger.info("wait 10 seconds to let chrome load the webpage")
        time.sleep(10)

        element = driver.find_element(By.XPATH, "//button[@id='load-button']")
        ActionChains(driver).move_to_element(element).perform()
        element.click()

        logger.info("Start DASH Live Streaming Test for {}".format(EXPERIMENT_ID))
        time.sleep(exp.ROUND_DURATION)
        logger.info("Streaming test completed")

        try:
            requests.post("http://stat-server/ping/stop")
        except:
            pass

        driver.quit()

    except exceptions.InvalidSessionIdException as e:
        logger.error(str(e))

    logger.info("generating figures")
    generate_plots(EXPERIMENT_ID, exp.ROUND_DURATION, exp.TARGET_LATENCY, exp.CONSTANT_VIDEO_BITRATE, exp.EMULATION)
