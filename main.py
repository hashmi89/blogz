from flask import Flask, request, redirect, render_template,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body
    
@app.route('/')
@app.route('/blog', methods=["GET", "POST"])
def blog():
    posts = Blog.query.all()

    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        title_error = ""
        blogpost_error = ""

        if title == "":
            title_error = "Please enter a title"
        
        if body == "":
            blogpost_error = "Please enter a body"
        
        if not title_error and not blogpost_error:
            newpost = Blog(title, body)
            db.session.add(newpost)
            db.session.commit()
            return redirect(url_for('blog'))
        else:
            return render_template('newpost.html', title_error=title_error, blogpost_error=blogpost_error)

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()