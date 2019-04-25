from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:dbAdmin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.Text)
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/blog')
def display_blog():
    post_id = request.args.get('id')
    if (post_id):
        ind_post = Blog.query.get(post_id)
        return render_template('ind_post.html', ind_post=ind_post)
    else:

        all_blog_posts = Blog.query.all()
        return render_template('blog.html', posts=all_blog_posts)

@app.route('/newpost', methods=['POST', 'GET'])
def add_entry():

    if request.method == 'POST':

        title_arg_error = ""
        post_arg_error = ""

        title_arg = request.form['blog_title']
        post_arg = request.form['blog_post']
        post_new = Blog(title_arg, post_arg)

        if title_arg != "" and post_arg != "":

            db.session.add(post_new)
   
            db.session.commit()
            post_link = "/blog?id=" + str(post_new.id)
            return redirect(post_link)
        else:
            if title_arg == "" and post_arg == "":
                title_arg_error = "Please enter text for blog title"
                post_arg_error = "Please enter text for blog entry"
                return render_template('new_post.html', blog_entry_error=post_arg_error, title_error=title_arg_error)
            elif title_arg == "":
                title_arg_error = "Please enter text for blog title"
                return render_template('new_post.html', title_error=title_arg_error, post_entry=post_arg)
            elif post_arg == "":
                post_arg_error = "Please enter text for blog entry"
                return render_template('new_post.html', blog_entry_error=post_arg_error, post_title=title_arg)

    else:
        return render_template('new_post.html')
        
if __name__ == '__main__':
    app.run()