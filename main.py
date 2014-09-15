import webapp2, jinja2, os
from webapp2_extras import routes
from models import User, Transaction, R, P
import json as simplejson
import logging
import urllib
import urllib2
import time
import datetime, random, string
import hashlib
import base64
import facebook
from functions import *
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from settings import SETTINGS
from settings import SECRET_SETTINGS

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)


def login_required(fn):
    '''So we can decorate any RequestHandler with #@login_required'''
    def wrapper(self, *args):
        if not self.user:
            self.redirect(self.uri_for('www-login', referred=self.request.path))
        else:
            return fn(self, *args)
    return wrapper


def admin_required(fn):
    '''So we can decorate any RequestHandler with @admin_required'''
    def wrapper(self, *args):
        if not self.user:
            self.redirect(self.uri_for('www-login'))
        elif self.user.status == "admin":
            return fn(self, *args)
        else:
            self.redirect(self.uri_for('www-front'))
    return wrapper


def hash_password(email, password):
    i = email + password + SECRET_SETTINGS["password_salt"]
    return base64.b64encode(hashlib.sha1(i).digest())


""" jinja environment functions """

def get_user(key):
    user = ndb.Key(urlsafe=key).fetch()
    return user

jinja_environment.filters['get_user'] = get_user




"""Request Handlers Start Here"""


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        self.now = datetime.datetime.now()
        self.tv = {}
        self.settings = SETTINGS.copy()
        self.initialize(request, response)
        self.has_pass = False
        self.tv["version"] = os.environ['CURRENT_VERSION_ID']
        self.local = False
        if "127.0.0.1" in self.request.uri or "localhost" in self.request.uri:  
            self.local = True
        # misc
        self.tv["current_url"] = self.request.uri
        self.tv["fb_login_url"] = facebook.generate_login_url(self.request.path, self.uri_for('www-fblogin'))

        if "?" in self.request.uri:
            self.tv["current_base_url"] = self.request.uri[0:(self.request.uri.find('?'))]
        else:
            self.tv["current_base_url"] = self.request.uri

        try:
            self.tv["safe_current_base_url"] = urllib.quote(self.tv["current_base_url"])
        except:
            logging.exception("safe url error")

        self.tv["request_method"] = self.request.method

        self.session = self.get_session()
        self.user = self.get_current_user()


    def render(self, template_path=None, force=False):
        self.tv["current_timestamp"] = time.mktime(self.now.timetuple())
        self.settings["current_year"] = self.now.year
        self.tv["settings"] = self.settings

        self.tv["date_today"] = datetime.datetime.now().strftime("%m/%d/%Y")

        if self.request.get('error'):
            self.tv["error"] = self.request.get("error").strip()
        if self.request.get('success'):
            self.tv["success"] = self.request.get("success").strip()
        if self.request.get('warning'):
            self.tv["warning"] = self.request.get("warning").strip()

        if self.user:
            self.tv["user"] = self.user.to_object()

        if self.request.get('json') or not template_path:
            self.response.out.write(simplejson.dumps(self.tv))
            return

        template = jinja_environment.get_template(template_path)
        self.response.out.write(template.render(self.tv))
        logging.debug(self.tv)


    def get_session(self):
        from gaesessions import get_current_session
        return get_current_session()


    def get_current_user(self):
        if self.session.has_key("user"):
            user = User.get_by_id(self.session["user"])
            return user
        else:
            return None


    def login(self, user):
        self.session["user"] = user.key.id()
        return

    def login_fb(self, fb_content, access_token):
        self.logout()
        user = User.query(User.fb_id == fb_content["id"]).get()
        if not user:
            email = fb_content["email"]
            if email:
                user = User.query(User.email == email).get()

            if user:
                # Merge User

                user.fb_id = fb_content["id"]
                try:
                    user.fb_username = fb_content["username"]
                except:
                    logging.exception("no username?")
                user.first_name = fb_content["first_name"]
                try:
                    user.last_name = fb_content["last_name"]
                except:
                    logging.exception("no last_name?")
                try:
                    user.middle_name = fb_content["middle_name"]
                except:
                    logging.exception('no middle name?')

                user.name = user.first_name
                if user.middle_name:
                    user.name += " " + user.middle_name

                if user.last_name:
                    user.name += " " + user.last_name

                try:
                    user.fb_access_token = access_token
                except:
                    logging.exception('no access token')
            else:
                user = User(id=email)
                user.fb_id = fb_content["id"]
                try:
                    user.fb_username = fb_content["username"]
                except:
                    logging.exception("no username?")
                user.email = fb_content["email"]
                user.first_name = fb_content["first_name"]
                try:
                    user.last_name = fb_content["last_name"]
                except:
                    logging.exception("no last_name?")
                try:
                    user.middle_name = fb_content["middle_name"]
                except:
                    logging.exception('no middle name?')

                user.name = user.first_name
                if user.middle_name:
                    user.name += " " + user.middle_name

                if user.last_name:
                    user.name += " " + user.last_name

                try:
                    user.fb_access_token = access_token
                except:
                    logging.exception('no access token')

            user.put()
        self.login(user)
        return


    def logout(self):
        if self.session.is_active():
            self.session.terminate()
            return


    def iptolocation(self):
        country = self.request.headers.get('X-AppEngine-Country')
        logging.info("COUNTRY: " + str(country))
        if country == "GB":
            country = "UK"
        if country == "ZZ":
            country = ""
        if country is None:
            country = ""
        return country



class FrontPage(BaseHandler):
    def get(self):
        if self.user:
            self.redirect(self.uri_for('www-dashboard'))
            return

        self.tv["current_page"] = "FRONT"
        self.render('frontend/front.html')


class RegisterPage(BaseHandler):
    def get(self):
        if self.user:
            self.redirect(self.uri_for('www-dashboard', referred="register"))
            return

        self.tv["current_page"] = "REGISTER"
        self.render('frontend/register.html')


    def post(self):
        if self.user:
            self.redirect(self.uri_for('www-dashboard'))
            return

        if self.request.get("password") != self.request.get("confirm_password"):
            self.redirect(self.uri_for('www-register', error = "Password does not match!."))
            return

        if self.request.get('email') and self.request.get('password') and self.request.get('name'):
            email = self.request.get('email').strip().lower()
            name = self.request.get('name').strip()
            password = self.request.get('password')
            user = User.query(User.email == email).fetch(1)
            if user:
                self.redirect(self.uri_for('www-login', error = "User already exists. Please log in."))
                return
            while True:
                code_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
                myuser = User.get_by_id(code_id)
                if not myuser:
                    break

            user = User(id=code_id)
            user.password = hash_password(email, password)
            user.email = email
            user.name = name
            user.code_id = code_id
            user.phonenumber = self.request.get("phonenumber")
            user.put()
            self.login(user)
            if self.request.get('goto'):
                self.redirect(self.request.get('goto'))
            else:
                self.redirect(self.uri_for('www-dashboard'))
            return
        else:
            self.redirect(self.uri_for('www-register', error = "Please enter all the information required."))


class Logout(BaseHandler):
    def get(self):
        if self.user:
            self.logout()
        self.redirect(self.uri_for('www-login', referred="logout"))


class LoginPage(BaseHandler):
    def get(self):
        if self.user:
            self.redirect(self.uri_for('www-dashboard', referred="login"))
            return

        if self.request.get('email'):
            self.tv["email"] = self.request.get("email").strip()

        self.tv["current_page"] = "LOGIN"
        self.render('frontend/login.html')


    def post(self):
        if self.user:
            self.redirect(self.uri_for('www-dashboard'))
            return

        if self.request.get('email') and self.request.get('password'):
            email = self.request.get('email').strip().lower()
            password = self.request.get('password')
            #user = User.get_by_id(email)
            myuser = User.query(User.email == email).fetch(1)

            if not myuser:
                self.redirect(self.uri_for('www-login', error="User not found. Please try another email or register."))
                return
            user = myuser[0]
            if user.password == hash_password(email, password):
                self.login(user)
                if self.request.get('goto'):
                    self.redirect(self.request.get('goto'))
                else:
                    self.redirect(self.uri_for('www-dashboard'))
                return
            else:
                self.redirect(self.uri_for('www-login', error="Wrong password. Please try again.", email=email))
                return
        else:
            self.redirect(self.uri_for('www-login', error="Please enter your email and password."))


class FBLoginPage(BaseHandler):
    def get(self):
        if not self.settings["enable_fb_login"]:
            self.redirect(self.uri_for("www-login"))
            return

        if self.user:
            self.redirect(self.uri_for('www-dashboard', referred="fblogin"))
            return

        if self.request.get('code') and self.request.get('state'):
            state = self.request.get('state')
            code = self.request.get('code')
            access_token = facebook.code_to_access_token(code, self.uri_for('www-fblogin'))
            if not access_token:
                # Assume expiration, just redirect to login page
                self.redirect(self.uri_for('www-login', referred="fblogin", error="We were not able to connect with Facebook. Please try again."))
                return

            url = "https://graph.facebook.com/me?access_token=" + access_token

            result = urlfetch.fetch(url)
            if result.status_code == 200:
                self.login_fb(simplejson.loads(result.content), access_token)
                self.redirect(str(state))
                return

        else:
            self.redirect(facebook.generate_login_url(self.request.get('goto'), self.uri_for('www-fblogin')))


class DashboardPage(BaseHandler):
    @login_required
    def get(self):
        if self.user.status == "user":
            self.tv["current_page"] = "DASHBOARD"
            self.render('frontend/dashboard.html')
        elif self.user.status == "admin":
            self.tv["current_page"] = "ADMIN DASHBOARD"

            trans = Transaction.query().order(-Transaction.created).fetch(100)

            self.tv["transactions"] = trans

            self.render('frontend/dashboard-admin.html')


class TransactionPage(BaseHandler):
    @admin_required
    def get(self):
        if not self.request.get("trans_id"):
            self.tv["current_page"] = "TRANSACTION"
            self.tv["trans_id"] = get_trans_id()
            self.render("frontend/transactionpage.html")
            return

        self.tv["current_page"] = "TRANSACTION DETAILS"
        trans_id = self.request.get("trans_id")
        trans = Transaction.get_by_id(trans_id)

        parcel = P.query(P.trans_key == trans.key.urlsafe()).fetch(1)

        self.tv["parcel_code"] = parcel[0].codes
        self.tv["transaction"] = trans.to_object()
        self.render("frontend/trans-details.html")

    def post(self):
        trans = Transaction(id=self.request.get("trans_code"))
        trans.trans_code = self.request.get("trans_code")

        sender = User.get_by_id(self.request.get("sender_code"))
        trans.sender = sender.key.urlsafe()
        
        receiver = User.get_by_id(self.request.get("receiver_code"))
        trans.receiver = receiver.key.urlsafe()

        trans.description = self.request.get("description")
        logging.critical(self.request.get("eda"))
        date = datetime.datetime.strptime(self.request.get("eda"), '%m/%d/%Y')
        logging.critical(date)
        trans.eda = date
        p_code = ""
        r_code = ""
        while True:
            p_code = parser_code()
            parcel = P.get_by_id(p_code)    
            if not parcel:
                break;

        while True:
            r_code = receiver_code()
            receiver = R.get_by_id(r_code)
            if not receiver:
                break;

        logging.critical(p_code)
        logging.critical(r_code)

        trans.parser_code = hash_code(p_code, "PARSER")
        trans.receiver_code = hash_code(r_code, "RECEIVER")

        trans.put()

        """ save transaction for PARSEL code """
        p = P(id=p_code)
        p.codes = p_code
        p.trans_key = trans.key.urlsafe()
        p.put()
        """ ---------------------------------- """

        """ save transaction for RECEIVER code """
        r = R(id=r_code)
        r.codes = r_code
        r.trans_key = trans.key.urlsafe()
        r.put()
        """ ---------------------------------- """

        self.redirect(self.uri_for('www-login', success="Added!."))

class GetUser(BaseHandler):
    @admin_required
    def post(self):
        user = User.get_by_id(self.request.get("user_id"))
        if user:
            data = user.to_object()
        else:
            data = ""

        self.response.out.write(simplejson.dumps(data))


class OpenSB(BaseHandler):
    def post(self):
        server_base_url = SECRET_SETTINGS["server_base_url"]
        datas = {}
        if self.request.get("code"):
            hashCode = hash_code(self.request.get("code"), "RECEIVER")
            logging.critical(hashCode)

            trans = Transaction.query(Transaction.receiver_code == hashCode).fetch(1)


            if trans:
                if trans[0].status == "received":
                    datas["status"] = "ok"
                    datas["error_code"] = "202"
                    datas["message"] = "This transaction is does not exist!."
                    self.response.out.write(simplejson.dumps(datas))
                    return

                url = server_base_url + "/open/0"
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                
                """ change transaction status to DELIVERED """
                trans[0].status = "received"
                trans[0].put()
                """ -------------------------------------- """

                """ send email to the sender """
                sender = ndb.Key(urlsafe=trans[0].sender).get()
                send_email_to_sender(sender.to_object(), trans[0].to_object())
                """ -------------------------------------- """

                datas["status"] = "ok"
                datas["error_code"] = "200"
                datas["message"] = "Package is now claimed! Thanks for using zbox"
                self.response.out.write(simplejson.dumps(datas))
                return
            else:
                hashCode = hash_code(self.request.get("code"), "PARSER")
                trans = Transaction.query(Transaction.parser_code == hashCode).fetch(1)
                datas = {}

                if trans:
                    if trans[0].status == "ready for pickup":
                        datas["status"] = "ok"
                        datas["error_code"] = "202"
                        datas["message"] = "This transaction is now ready for pickup"
                        self.response.out.write(simplejson.dumps(datas))
                        return

                    try:
                        url = server_base_url + "/open/1"
                        req = urllib2.Request(url)
                        response = urllib2.urlopen(req)

                        """ change transaction status to DELIVERED """
                        trans[0].status = "ready for pickup"
                        trans[0].put()
                        """ -------------------------------------- """

                        """ send email to the receiver """
                        receiver = ndb.Key(urlsafe=trans[0].receiver).get()
                        send_email_to_receiver(receiver.to_object(), trans[0].to_object())

                        """ -------------------------------------- """


                        datas["status"] = "ok"
                        datas["error_code"] = "200"
                        datas["message"] = "successsfully delivered"
                        self.response.out.write(simplejson.dumps(datas))
                        return                        
                    except:
                        datas["status"] = "error"
                        datas["error_code"] = "201"
                        datas["message"] = "server is down! you can try again later or contact the administrator!.."
                        self.response.out.write(simplejson.dumps(datas))
                        return
                else:
                    datas["status"] = "error"
                    datas["error_code"] = "201"
                    datas["message"] = "Transaction Does not Exist!.."
                    self.response.out.write(simplejson.dumps(datas))
                    return


class ProfileHandler(BaseHandler):
    def get(self):
        self.tv["current_page"] = "PROFILE"
        self.render("frontend/profile.html")

    def post(self):
        name = self.request.get("name")
        alt_email = self.request.get("email")
        phone = self.request.get("phone")

        self.user.name = name
        self.user.alternative_email = alt_email
        self.user.phonenumber = phone

        self.user.put()
        self.redirect(self.uri_for('www-profile', success="Added! ."))


class SetSBHandler(BaseHandler):
    def post(self):
        sb = self.request.get("sb")
        self.user.speedbox = sb

        self.user.put()
        self.redirect(self.uri_for('www-dashboard', success="Added! ."))    

class ErrorHandler(BaseHandler):
    def get(self, page):
        self.tv["current_page"] = "ERROR"
        self.render('frontend/dynamic404.html')


class KeyPadPage(BaseHandler):
    def get(self):
        self.render('frontend/keypad.html')


site_domain = SETTINGS["site_domain"].replace(".","\.")

app = webapp2.WSGIApplication([
    routes.DomainRoute(r'<:' + site_domain + '|localhost|' + SETTINGS["app_id"] + '\.appspot\.com>', [
        webapp2.Route('/', handler=FrontPage, name="www-front"),
        webapp2.Route('/register', handler=RegisterPage, name="www-register"),
        webapp2.Route('/transaction', handler=TransactionPage, name="www-transaction"),
        webapp2.Route('/dashboard', handler=DashboardPage, name="www-dashboard"),
        webapp2.Route('/logout', handler=Logout, name="www-logout"),
        webapp2.Route('/profile', handler=ProfileHandler, name="www-profile"),
        webapp2.Route('/getuser', handler=GetUser, name="www-getuser"),
        webapp2.Route('/set/sb', handler=SetSBHandler, name="www-setsb"),
        webapp2.Route('/open/sb', handler=OpenSB, name="www-sb"),
        webapp2.Route('/login', handler=LoginPage, name="www-login"),
        webapp2.Route('/keypad', handler=KeyPadPage, name="www-keypad"),
        webapp2.Route('/fblogin', handler=FBLoginPage, name="www-fblogin"),
        webapp2.Route(r'/<:.*>', ErrorHandler)
    ])
])