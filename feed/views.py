import copy
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from feed.forms import PostForm
from models import Post, User


# CONFIG
feed_blueprint = Blueprint('feed', __name__, template_folder='templates')


@feed_blueprint.route('/feed')
@login_required
@requires_roles('user')
def feed():
    posts = Post.query.order_by(desc('id')).all()

    decrypted_posts = []

    for p in posts:
        user = User.query.filter_by(username=p.username).first()
        dec_post = copy.deepcopy(p)
        dec_post.view_post(user.postkey)
        decrypted_posts.append(dec_post)

    return render_template('feed.html', posts=decrypted_posts)


@feed_blueprint.route('/create', methods=('GET', 'POST'))
@login_required
@requires_roles('user')
def create():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(username=current_user.username, title=form.title.data, body=form.body.data, postkey=current_user.postkey)

        db.session.add(new_post)
        db.session.commit()

        return blog()
    return render_template('create.html', form=form)


@feed_blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@requires_roles('user')
def update(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        return render_template('500.html')

    form = PostForm()

    if form.validate_on_submit():
        post.update_post(form.title.data, form.body.data, current_user.postkey)
        db.session.commit()
        return blog()

    post.view_post(current_user.postkey)

    form.title.data = post.title
    form.body.data = post.body

    return render_template('update.html', form=form)


@feed_blueprint.route('/<int:id>/delete')
@login_required
@requires_roles('user')
def delete(id):
    Post.query.filter_by(id=id).delete()
    db.session.commit()

    return blog()