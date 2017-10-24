from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Julia@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400))
    body = db.Column(db.String(10000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.args:
        id = request.args.get('id')
        entry = Blog.query.filter_by(id=id).first()
        headline = entry.title
        body = entry.body
        return render_template('entry.html', title="Blog Entry", headline=headline, body=body)

    entries = Blog.query.all()
    return render_template('blog.html',title="Blog", 
        entries=entries)


@app.route('/newpost', methods=['POST', 'GET'])
def create_new_entry():
    headline = ""
    body = ""
    if request.method == 'POST':
        headline = request.form['headline']
        body = request.form['body']
        if headline and body:
            new_entry = Blog(headline, body)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog')
        elif not headline:
            flash('Please add a title.', 'error')
        elif not body:
            flash('Please add content!', 'error')
    return render_template('newpost.html', title="New Post", headline=headline, body=body)



if __name__ == '__main__':
    app.run()