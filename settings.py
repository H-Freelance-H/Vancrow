SETTINGS = {
    "app_id": "michaelivantogeno",
    "site_domain": "www.michaelivantogeno.appspot.com",
    "site_name": "SpeedBox",
    "start_year": 2013,
    "enable_fb_login": True,
    "fb_id": "",
    "fb_secret": "",
    "fb_permissions": ["email"],
    "fb_app_access_token": "",
    "pubnub_subscriber_token": "",
    "pubnub_publisher_token": "",
    "pubnub_secret_key": "",
    "password_salt": "ENTER_SALT_HERE"  # Only set once. Do NOT change. If changed, users will not be able to login
}

SECRET_SETTINGS = {
    "fb_secret": "",
    "fb_app_access_token": "",
    "pubnub_secret_key": "",
    "server_base_url": "http://192.168.1.125:8080",
    "password_salt": "Pom64EaUrTAEjrsKqrhuAfNcW4U=LWdvZXM()ta$GVyZXIUCxIEV/#XNl.",  # Only set once. Do NOT change. If changed, users will not be able to login
    "mandrill_key": "VOGMtY1YpD0bNmMIt2bMPQ"
}


SB_BOXES = {
    
    "sb_1": "small",
    "sb_2": "small",
    "sb_3": "small",
    "sb_4": "small",
    "sb_5": "medium",
    "sb_6": "medium",
    "sb_7": "medium",
    "sb_8": "medium",
    "sb_9": "large",
    "sb_10": "large",
    "sb_11": "large",
    "sb_12": "large",
    "sb_13": "xlarge",
    "sb_14": "xlarge",
    "sb_15": "xlarge",
    "sb_16": "xlarge"
}



# Local Settings
import os
def development():
    if os.environ['SERVER_SOFTWARE'].find('Development') == 0:
        return True
    else:
        return False


if development():
    SETTINGS["fb_id"] = "569550796388888"
    SECRET_SETTINGS["fb_secret"] = "be20b1c85858844bf561c82e139b25e8"
    SECRET_SETTINGS['fb_app_access_token'] = "539310509418887|dPefXXFnqaygLJ8RxWG_-9Xm9JY"