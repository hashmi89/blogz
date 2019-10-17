from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'MySecretKey'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'blog_itself', 'index', 'singleuser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/blog')
        elif user and user.password != password:
            flash('Password is incorrect', 'error')
        else:
            flash('Username does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if not username and not password and not verify:
            flash('One or more fields are invalid', 'error')
        elif password != verify:
            flash('Passwords do not match', 'error')
        elif len(username) or len(password) < 3 and len(username) or len(password) >20:
            flash('Username and Password out of range (3-20)', 'error')
        elif not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            flash('Username already exists', 'error')
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect(url_for('index'))

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    posts = Blog.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ""
        blogpost_error = ""

        if title == "":
            title_error = "Please enter a title"
        
        if body == "":
            blogpost_error = "Please enter a body"
        
        if not title_error and not blogpost_error:
            newpost = Blog(title, body, owner)
            db.session.add(newpost)
            db.session.commit()
            return redirect('/blog')
        else:
            return render_template('newpost.html', title_error=title_error, blogpost_error=blogpost_error)

    else:
        return render_template('newpost.html')

@app.route('/user/<username>')
def singleuser(username):
    user = User.query.filter_by(username=username).first()
    posts = Blog.query.filter_by(owner=user).all()
    return render_template('singleUser.html', user=user, posts=posts)

@app.route("/blog/<blog_id>")
def blog_itself(blog_id):
    post = Blog.query.get_or_404(blog_id)
    return render_template('blog_itself.html', post=post)

if __name__ == '__main__':
    app.run()