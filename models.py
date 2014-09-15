from google.appengine.ext import ndb
import time


class User(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    fb_id = ndb.StringProperty()
    fb_access_token = ndb.StringProperty()
    fb_username = ndb.StringProperty()
    name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    middle_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phonenumber = ndb.StringProperty()
    code_id = ndb.StringProperty()
    speedbox = ndb.StringProperty()
    alternative_email = ndb.StringProperty()
    status = ndb.StringProperty(default='user')

    def to_object(self):
        details = {}
        details["created"] = int(time.mktime(self.created.timetuple()))
        details["updated"] = int(time.mktime(self.updated.timetuple()))
        details["email"] = self.email
        details["name"] = self.name
        details["code_id"] = self.code_id
        details["status"] = self.status
        details["phone"] = self.phonenumber
        details["alt_email"] = self.alternative_email
        details["speedbox"] = self.speedbox

        return details


class Transaction(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    trans_code = ndb.StringProperty()
    sender = ndb.StringProperty()
    receiver = ndb.StringProperty()
    description = ndb.TextProperty()
    status = ndb.StringProperty(default="undelivered")
    eda = ndb.DateTimeProperty()
    parser_code = ndb.StringProperty()    
    receiver_code = ndb.StringProperty()
    sync_status = ndb.BooleanProperty(default=False)
    zbox = ndb.StringProperty()
    box_number = ndb.StringProperty()

    def to_object(self):
        details = {}
        details["created"] = str(self.created.strftime("%m/%d/%Y"))
        details["updated"] = str(self.created)
        details["trans_code"] = self.trans_code
        details["key"] = self.key.urlsafe()
        sender = ndb.Key(urlsafe=self.sender).get()
        details["sender"] = sender.to_object()  

        receiver = ndb.Key(urlsafe=self.receiver).get()
        details["receiver"] = receiver.to_object()

        details["description"] = self.description
        details["status"] = self.status
        details["eda"] = self.eda

        return details


""" Receiver Code """
class R(ndb.Model):
    codes = ndb.StringProperty()
    trans_key = ndb.StringProperty()


""" Parser Code """
class P(ndb.Model):
    codes = ndb.StringProperty()
    trans_key = ndb.StringProperty()


class SpeedBox(ndb.Model):
    speedbox = ndb.StringProperty()
    address = ndb.StringProperty()
    box_count = ndb.IntegerProperty()
    box_available = ndb.StringProperty(repeated=True)
    box_vacant = ndb.StringProperty(repeated=True)
    sb_server = ndb.StringProperty()


class Parcel(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()


