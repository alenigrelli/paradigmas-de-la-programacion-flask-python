from flask import render_template, request, jsonify
from peewee import *
from app import app, database
from models import User, Feed
from flask.ext.login import current_user
from auth import *
import feedparser


@app.route("/")
def main():
    if current_user.is_anonymous:
        return render_template("login.html")
    else:
        return redirect(url_for('index'))


@app.route("/login/<provider>")
def login(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = SignIn.get_provider(provider)
    return oauth.login()


@app.route("/callback/<provider>")
def callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = SignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        return redirect(url_for('main'))
    user, _ = User.get_or_create(
        social_id=social_id,
        nickname=username,
        email=email)
    login_user(user)
    return redirect(url_for('index'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main'))


@app.route("/index")
@login_required
def index():
    return render_template("index.html")


@app.route("/new_feed", methods=['POST'])
@login_required
def new_feed():
    feedurl = request.form['feed_url']
    f = feedparser.parse(feedurl)
    if f.bozo == 1:
        return jsonify(status='FAIL')
    if 'title' not in f.feed:
        return jsonify(status='FAIL')
    title = f.feed.title
    try:
        description = f.feed.description
    except AttributeError:
        description = ""
    Feed.create(
        user=current_user.id,
        title=title,
        url=feedurl,
        description=description)
    return jsonify(status='OK')


@app.route("/delete_feed", methods=['POST'])
@login_required
def delete_feed():
    feed = request.form['feed']
    try:
        fd = Feed.get(Feed.id == feed, Feed.user == current_user.id)
        fd.delete_instance()
        return jsonify(status='OK')
    except Feed.DoesNotExist:
        return jsonify(status='FAIL')


@app.route("/rss/<feed>")
@login_required
def rss(feed):
    try:
        fd = Feed.get(Feed.id == feed, Feed.user == current_user.id)
        return render_template("rss.html",
                               feed=fd,
                               entries=feedparser.parse(fd.url).entries)
    except Feed.DoesNotExist:
        abort(404)


@app.errorhandler(404)
def not_found(exc):
    return render_template("notfound.html"), 404

if __name__ == "__main__":
    database.create_tables([User, Feed], safe=True)
    app.run()
