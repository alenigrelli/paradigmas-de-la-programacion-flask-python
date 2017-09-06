from flask import redirect, url_for, session, abort
from flask_oauthlib.client import OAuth
from app import app
from models import User
from flask.ext.login import (LoginManager, login_required,
                             logout_user, login_user)

oauth = OAuth(app)
login_manager = LoginManager()
login_manager.init_app(app)

github = oauth.remote_app(
    'github',
    consumer_key='4c2a197a8b494722d7be',
    consumer_secret='1a1b15613e7fb6f4ccc3f5f61e27e26c2a3fd3aa',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

google = oauth.remote_app(
    'google',
    consumer_key=(
        "100074576936-07bcar152vcuok1muu9e4ki8q6u959b8"
        ".apps.googleusercontent.com"),
    consumer_secret="m2swxVcYr7snV4wNGGX97I8F",
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

dropbox = oauth.remote_app(
    'dropbox',
    consumer_key='rzgoghd4x1b6c6t',
    consumer_secret='re6mwc291hsd53b',
    request_token_params={},
    base_url='https://www.dropbox.com/1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.dropbox.com/1/oauth2/token',
    authorize_url='https://www.dropbox.com/1/oauth2/authorize',
)

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key='77wn6bxtm0z70p',
    consumer_secret='CbhDjThUBp6itndW',
    request_token_params={
        'scope': 'r_basicprofile',
        'state': 'RandomString'},
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

bitbucket = oauth.remote_app(
    'bitbucket',
    consumer_key='YuVU8hTZXmbcSfrm7k',
    consumer_secret='PXz6BjSqQXF2dDEqet8tGXf8y5aDGHLL',
    request_token_params={'scope': 'email'},
    base_url='https://api.bitbucket.org',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://bitbucket.org/site/oauth2/access_token',
    authorize_url='https://bitbucket.org/site/oauth2/authorize',
)


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query


class SignIn(object):
    providers = None

    def __init__(self, provider, get, id="id", name="name", email="email"):
        self.provider_name = provider
        self.get_info = get
        self.id = id
        self.name = name
        self.email = email

    def login(self):
        return self.service.authorize(callback=self.get_callback_url())

    def callback(self):
        resp = self.service.authorized_response()
        if resp is None:
            return (None, None, None)
        session[self.provider_name + "_token"] = (resp['access_token'], '')
        dat = self.service.get(self.get_info)
        id = "{}${}".format(self.provider_name, dat.data[self.id])
        if not self.email:
            email = ""
        else:
            email = dat.data[self.email]
        return (id, dat.data[self.name], email)

    def get_callback_url(self):
        return url_for('callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GithubSignIn(SignIn):
    def __init__(self):
        super(GithubSignIn, self).__init__('github',
                                           get='user')
        self.service = github


class GoogleSignIn(SignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google',
                                           get='userinfo')
        self.service = google


class DropboxSignIn(SignIn):
    def __init__(self):
        super(DropboxSignIn, self).__init__('dropbox',
                                            get='account/info',
                                            id='uid',
                                            name='display_name')
        self.service = dropbox


class LinkedinSignIn(SignIn):
    def __init__(self):
        super(LinkedinSignIn, self).__init__('linkedin',
                                             get='people/~',
                                             name='firstName',
                                             email="")
        self.service = linkedin


class BitbucketSignIn(SignIn):
    def __init__(self):
        super(BitbucketSignIn, self).__init__('bitbucket',
                                              get='2.0/user',
                                              id='uuid',
                                              name='display_name',
                                              email="")
        self.service = bitbucket


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@dropbox.tokengetter
def get_dropbox_oauth_token():
    return session.get('dropbox_token')


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')


@bitbucket.tokengetter
def get_bitbucket_oauth_token():
    return session.get('bitbucket_token')


@login_manager.user_loader
def load_user(uid):
    try:
        return User.get(User.id == uid)
    except User.DoesNotExist:
        session.clear()
        return AnonymousUser()


@login_manager.unauthorized_handler
def unauthorized():
    return abort(404)
