import base64
import copy
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from posts.forms import PostForm
from models import Post, User


# CONFIG
posts_blueprint = Blueprint('posts', __name__, template_folder='templates')


# VIEWS
# view posts page
@posts_blueprint.route('/posts')
@login_required
def posts():
    # get all posts in descending ordered depending on their id number
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

    # re-render posts page with the decrypted posts
    return render_template('posts.html', posts=decrypted_posts)


# view individual post
@posts_blueprint.route('/<int:id>/posts')
@login_required
def post(id):
    # get all posts in descending ordered depending on their id number
    post = Post.query.get_or_404(id)

    # create post copy
    post_copy = copy.deepcopy(post)

    # decrypt copy of the current_winning_draw
    user = User.query.filter_by(email=post.email).first()
    post_copy.view_post(user.postkey)

    # re-render posts page with the decrypted posts
    return render_template('post.html', post=post_copy)


# render picture admin uploads
def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


# create a new post
@posts_blueprint.route('/create_post', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = PostForm()

    # if form valid
    if form.validate_on_submit():
        file = request.files['inputFile']
        data = file.read()
        render_file = render_picture(data)

        # create a new post with the form data
        new_post = Post(email=current_user.email,
                        title=form.title.data,
                        body=form.body.data,
                        image=render_file,
                        postkey=current_user.postkey)

        # add the new post to the database
        db.session.add(new_post)
        db.session.commit()
        # send admin to post page with the matching 'id'
        flash("Post Created Successfully")
        return redirect(url_for('posts.post', id=new_post.id))

    # re-render create_post page
    return render_template('create_post.html', form=form)


# update or edit a post
@posts_blueprint.route('/<int:id>/update_post', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
    # get draw with the matching id
    post = Post.query.filter_by(id=id).first()

    # if post with given id does not exist
    if not post:
        # re-render Internal Server Error page
        return render_template('500.html')

    # create Post object
    form = PostForm()

    # if form valid
    if form.validate_on_submit():
        # update old post data with the new form data and commit it to database
        post.update_post(form.title.data, form.body.data, current_user.postkey)
        db.session.commit()
        flash("Post Updated Successfully")
        # send admin to post page with the matching 'id'
        return redirect(url_for('posts.post', id=post.id))

    # creates a copy of post object which is independent of database
    post_copy = copy.deepcopy(post)

    # decrypt copy of post object
    post_copy.view_post(current_user.postkey)

    # set update form with title and body of copied post object
    form.title.data = post_copy.title
    form.body.data = post_copy.body

    # re-render update_post template
    return render_template('update_post.html', form=form)


# delete a post
@posts_blueprint.route('/<int:id>/delete_post')
@login_required
@requires_roles('admin')
def delete(id):
    # delete post which id matches
    Post.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Post has been deleted")
    return posts()
