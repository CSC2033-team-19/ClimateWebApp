import copy
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from posts.forms import PostForm
from models import Post, User


# CONFIG
posts_blueprint = Blueprint('posts', __name__, template_folder='templates')


@posts_blueprint.route('/posts')
@login_required
def posts():
    posts = Post.query.order_by(desc('id')).all()

    # creates a list of copied post objects which are independent of database.
    post_copies = list(map(lambda x: copy.deepcopy(x), posts))

    # empty list for decrypted copied post objects
    decrypted_posts = []

    # decrypt each copied post object and add it to decrypted_posts array.
    for p in post_copies:
        user = User.query.filter_by(email=p.email).first()
        p.view_post(user.postkey)
        decrypted_posts.append(p)

    return render_template('posts.html', posts=decrypted_posts)


@posts_blueprint.route('/create_post', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(email=current_user.email, title=form.title.data, body=form.body.data, postkey=current_user.postkey)

        db.session.add(new_post)
        db.session.commit()

        return posts()
    return render_template('create_post.html', form=form)


@posts_blueprint.route('/<int:id>/update_post', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        return render_template('500.html')

    form = PostForm()

    if form.validate_on_submit():
        post.update_post(form.title.data, form.body.data, current_user.postkey)
        db.session.commit()
        return posts()

    # creates a copy of post object which is independent of database.
    post_copy = copy.deepcopy(post)

    # decrypt copy of post object.
    post_copy.view_post(current_user.postkey)

    # set update form with title and body of copied post object
    form.title.data = post_copy.title
    form.body.data = post_copy.body

    return render_template('update_post.html', form=form)


@posts_blueprint.route('/<int:id>/delete')
@login_required
@requires_roles('admin')
def delete(id):
    Post.query.filter_by(id=id).delete()
    db.session.commit()

    return posts()
