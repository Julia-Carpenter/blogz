from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Julia@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400))
    body = db.Column(db.String(10000))
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


#TODO Not sure if these are the only allowed routes
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'homepage', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def homepage():
    users=User.query.all()
    return render_template('index.html', users=users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if not user:
            flash('User does not exist', 'error')
        else:
            flash('User password incorrect', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data
        if not username or not password or not verify:
            flash("One or more fields are invalid", 'error')

        elif password != verify:
            flash("The passwords entered do not match.", 'error')

        elif len(password) <= 2:
            flash("password must exceed 2 characters", 'error')

        elif len(username) <= 2:
            flash("username must exceed 2 characters", 'error')

        #existing_user = User.query.filter_by(username=username).first()
        #if existing_user:
            #flash("The username <strong>{0}</strong> is already registered".format(username), 'error')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    return render_template('signup.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def index():
    owner = session['username']
    id = request.args.get('id')
    if id:
        entry = Blog.query.filter_by(id=id).first()
        headline = entry.title
        body = entry.body
        authorId = User.query.filter_by(username=owner).first()
        authorId = authorId.id
        return render_template('entry.html', title="Blog Entry", headline=headline, body=body, authorId=authorId)
    entries = Blog.query.all()
    userId = request.args.get('user')
    if userId:
        thisuser = User.query.filter_by(id=userId).first()
        return render_template('usersposts.html', title=userId, userId = userId, entries=entries, thisuser=thisuser)
    return render_template('blog.html',title="Blog", 
        entries=entries)


@app.route('/newpost', methods=['POST', 'GET'])
def create_new_entry():
    headline = ""
    body = ""
    user = ""
    if request.method == 'POST':
        headline = request.form['headline']
        body = request.form['body']
        #TODO the owner line below this might be wrong
        owner = User.query.filter_by(username=session['username']).first()
        if headline and body:
            new_entry = Blog(headline, body, owner)
            db.session.add(new_entry)
            db.session.commit()
            thisentry = Blog.query.order_by('-id').first()
            id = str(thisentry.id)
            return redirect('/blog?id=' + id)
        elif not headline:
            flash('Please add a title.', 'error')
        elif not body:
            flash('Please add content!', 'error')
    return render_template('newpost.html', title="New Post", headline=headline, body=body)



if __name__ == '__main__':
    app.run()