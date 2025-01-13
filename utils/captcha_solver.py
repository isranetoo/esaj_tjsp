
import os
import time
import base64
from io import BytesIO

import numpy as np

import pytesseract
from PIL import Image
from PIL import ImageFilter
from scipy.ndimage import gaussian_filter

from twocaptcha import TwoCaptcha
from twocaptcha.api import NetworkException
from twocaptcha.api import ApiException

from .logger_config import get_logger
from .credentials import get_twocapthca_token


LOGGER = get_logger('main_script')

# Check if running on windows computer and if so, adds pytesseract to path
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# ---------------------------------- Local Solvers ------------------------------------
def solve_captcha_normal_local(bytes_data, min_lenght: int = 6, max_length: int= 6,
                               th0: int = 185, th1: int = 105, sig1: int = 1.1,
                               th2: int = 105, sig2: int = 1.0) -> str:
    """ Attempts to solve captcha with pytesseract

    Args:
        bytes_data: image encoded as base64
        min_length: minimum number of chars in captcha, Defaults to 6
        max_length: maximum number of chars in captcha, Defaults to 6
        th0: erasing threshold 0, Defaults to 185
        sig1:  blurring sigma 1, Defaults to 1.1
        th1: erasing threshold 1, Defaults to 105
        sig2: blurring sigma 2, Defaults to 1.0
        th2: erasing threshold 2, Defaults to 105

    Returns:
        Captcha response
    """
    original = Image.open(BytesIO(base64.b64decode(bytes_data)))

    # converting to black and white
    black_and_white = original.convert("L")
    img_threshold_0 = black_and_white.point(lambda p: p > th0 and 255)

    # Blurs image and aplies new threshold 1
    img_blurred_1 = Image.fromarray(gaussian_filter(np.array(img_threshold_0), sigma=sig1))
    img_threshold_1 = img_blurred_1.point(lambda p: p > th1 and 255)
    img_ee_1 = img_threshold_1.filter(ImageFilter.EDGE_ENHANCE_MORE)
    img_shp_1 = img_ee_1.filter(ImageFilter.SHARPEN)

    # Blurs image and aplies new threshold 2
    blurred2 = Image.fromarray(gaussian_filter(np.array(img_shp_1), sigma=sig2))
    img_threshold_2 = blurred2.point(lambda p: p > th2 and 255)
    img_ee_2 = img_threshold_2.filter(ImageFilter.EDGE_ENHANCE_MORE)
    img_shp_2 = img_ee_2.filter(ImageFilter.SHARPEN)

    ocr_config = '--psm 11 --oem 3 -c tessedit_char_whitelist=123456789abcdefghijklmnpqrstuvxwyz'
    result = pytesseract.image_to_string(img_shp_2, config=ocr_config)
    result = result.strip().replace(chr(32), "").replace("\n", "")

    if min_lenght < len(result) < max_length:
        result = pytesseract.image_to_string(img_shp_1, config=ocr_config)
        return result.strip().replace(chr(32), "").replace("\n", "")
    return result


# ---------------------------------- Two Captcha Solvers ------------------------------------
TWOCAPTCHASOLVER = TwoCaptcha(get_twocapthca_token())


def solve_recaptcha_api(sitekey: str, url: str) -> str:
    """ Solves recaptcha captcha

    Argas:
        sitekey: recaptcha site key (can be found on site)
        url: url of the website

    Returns:
        Captcha response
    """
    result = TWOCAPTCHASOLVER.recaptcha(sitekey=sitekey, url=url)
    return result['code']


def solve_captcha_normal_api(bytes_data, min_lenght: int = 6, max_length: int= 6, case_sensitive: int = 0) -> str:
    """ Attempts to solve captcha with TwoCaptcha API

    Args:
        bytes_data: image encoded as base64
        min_length: minimum number of chars in captcha, Defaults to 6
        max_length: maximum number of chars in captcha, Defaults to 6
        case_sensitive: If the captcha may contain upper and lower case, Defaults to 0 (False)

    Returns:
        Captcha response
    """
    result = ""
    while result == "":
        try:
            result = TWOCAPTCHASOLVER.normal(bytes_data, minLen=min_lenght, maxLen=max_length, caseSensitive=case_sensitive)['code']
        except NetworkException as e:
            LOGGER.error(str(e))
            time.sleep(0.5)
            continue
        except ApiException as e:
            if "NO_SLOT" in str(e):
                LOGGER.error(str(e))
                time.sleep(10)
                continue
            raise e

    return result
