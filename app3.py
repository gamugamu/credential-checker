# coding: utf-8

from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
import oauth2

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

oauth = OAuth(app)

CONSUMER_KEY='qUqCpiM61QgeF8c1ll4gEsK5v'
CONSUMER_SECRET='ZEKy0bhAPzqtTOVloJb31GdnnBXQU0zsXsW9ohKx6Urtw7lQ2q'

twitter = oauth.remote_app(
    'twitter',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)


def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    consumer        = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token           = oauth2.Token(key=key, secret=secret)
    client          = oauth2.Client(consumer, token)
    resp, content   = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

@app.route("/test")
def test():
    print "session", session
    t_session           = session['twitter_oauth']
    twitter_oauth       = t_session['oauth_token']
    oauth_token_secret  = t_session['oauth_token_secret']
    print "check ", twitter_oauth, oauth_token_secret
    home_timeline = oauth_req('https://api.twitter.com/1.1/account/verify_credentials.json', twitter_oauth, oauth_token_secret)
    print "home", home_timeline
    return "done"

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        print "get_twitter_token", session
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/')
def index():
    tweets = None
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Unable to load tweets from Twitter.')
    return render_template('index.html', tweets=tweets)


@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })
    print "route tweet", session

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
        )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
