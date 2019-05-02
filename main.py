from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:dbAdmin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'kadjf4584958lsdkjf'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.Text)
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blog', 'index', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    all_users = User.query.distinct()
    return render_template('index.html', list_all=all_users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Make sure user and password inputs are not blank
        if username  == "" and password == "":
            flash('Username and password cannot be blank', 'error')
            return render_template('login.html')
        if username == "":
            flash('Username cannot be blank', 'error')
            return render_template('login.html')
        if password  == "":
            flash('Password cannot be blank', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()

        # Does user exist in database?
        if not user:
            flash('Username does not exist', 'error')
            return render_template('login.html')
            
        # Does password match database password?
        if user.password != password:
            flash('Incorrect Password', 'error')
            return render_template('login.html')

        session['username'] = username
        return redirect('newpost')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        userpw = request.form['password']
        userpwverify = request.form['password_validate']

        # Validate
        if username == "" and userpw == "":
            flash('Username and password fields are required', 'error')
            return render_template('signup.html')
        elif username == "":
            flash('Username is required', 'error')
            return render_template('signup.html')
        elif userpw == "":
            flash('Password is required', 'error')
            return render_template('signup.html')

        if userpw != userpwverify:
            flash('Passwords must match', 'error')
            return render_template('signup.html')

        if len(userpw) < 3 and len(username) < 3:
            flash('Username and password must be at least three characters', 'error')
            return render_template('signup.html')
        elif len(userpw) < 3:
            flash('Password must be at least three characters', 'error')
            return render_template('signup.html')
        elif len(username) < 3:
            flash('Username must be at least three characters', 'error')
            return render_template('signup.html')
        
        # Does user name already exist in database?
        existing_user = User.query.filter_by(username=username).first()
       
        # Add user if not in database, or create error message if it is.
        if not existing_user: 
            user_new = User(username, userpw)
            db.session.add(user_new)
            db.session.commit()
            session['username'] = username
            flash('New user added', 'success')
            return redirect('/newpost')
        else:
            flash('Invalid User name: name already exists', 'error')
            return render_template('signup.html')

    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog')
def display_blog():
    user_id = request.args.get('owner_id')
    if (user_id):
        single_user_posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('singleUser.html', posts = single_user_posts,
             user = single_user_posts[0].owner.username)
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
        owner = User.query.filter_by(username=session['username']).first()
        post_new = Blog(title_arg, post_arg, owner)

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