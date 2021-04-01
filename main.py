from flask import Flask, render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
from flask_paginate import Pagination,get_per_page_parameter,get_page_args
from forms import Register,Login,Enter_post
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_user,login_required,current_user,logout_user,UserMixin




with open('confiq.json', 'r') as c:
    values = json.load(c)["params"]

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = values['secretkey']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'register'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = values['gmail-user'],
    MAIL_PASSWORD = values['gmail-password'],
    MAIL_DEFAULT_SENDER = 'admin'
)
mail = Mail(app)


class Contact(db.Model):
    s_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    message = db.Column(db.String(120),nullable=False)
    phone_no=db.Column(db.Integer,nullable=False)
    email=db.Column(db.String(120),nullable=False)
    date=db.Column(db.String(50),nullable=True)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False,unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False,unique=True)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(12), default='default.jpg')
    post = db.relationship('Posts',backref='user',lazy=True)

    def __repr__(self):
        return f"Posts('{self.id}','{self.username}','{self.email}')"




class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    content=db.Column(db.String(200),nullable=False)
    subtitle = db.Column(db.String(200), nullable=True)
    date=db.Column(db.String(40),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Posts('{self.sno}','{self.title}','{self.user_id}')"



#route for homepage

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    post = Posts.query.order_by(Posts.sno.desc()).paginate(page=page, per_page=3)
    return render_template('index.html', value=values, post=post)


@app.route("/about")
def about():
    return render_template('about.html',value=values)

@app.route("/profile")
def profile():
    page = request.args.get('page', 1, type=int)
    post = Posts.query.filter_by(user_id=current_user.id).order_by(Posts.sno.desc()).paginate(page=page, per_page=3)
    return render_template('profile.html',value=values,post=post)



@app.route("/register",methods=['GET','POST'])
def register():
    form = Register()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,name=form.name.data,password=hashed_password,email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash("Account have been created successfully","success")
        return render_template('login.html', value=values, form=form)
    flash("Please enter valid credentials", "danger")
    return render_template('register.html',value=values,form=form)


#login as a admin
@app.route("/login",methods=['GET','POST'])
def login():
    form=Login()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user=User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("login successfully",category="success")
            return redirect(url_for('home'))
        return render_template('login.html', value=values, form=form)
    return render_template('login.html', value=values, form=form)


#enter a new post in admin mode
@app.route("/enterpost",methods=['GET','POST'])
def enterpost():
    form = Enter_post()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            post=Posts(title=form.title.data,content=form.content.data,subtitle=form.subtitle.data,date=datetime.now(),user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('enterpost.html', form=form, value=values)
    return redirect(url_for('login'))







#to create slug for every post
@login_required
@app.route("/post/<int:sno>",methods=['GET'])
def post_route(sno):
    if current_user.is_authenticated:
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('post.html',post=post,value=values)
    return redirect(url_for('login'))






#to send comment to the admin
@app.route("/contact",methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry = Contact(name=name,email=email,message=message,date=datetime.datetime.now()[0:20], phone_no=phone)
        db.session.add(entry)
        db.session.commit()
        """mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[values['gmail-user']],
                          body= message + "\n" + 'phone number='+ phone
                          )"""
    return render_template('contact.html',value=values)

@app.route("/login/edit/<string:sno>",methods=['GET','POST'])
def edit_post(sno):
        if (request.method == 'POST'):
            post=Posts.query.filter_by(sno=sno).first()
            Titleedit = request.form.get('eTitle')
            Subtitleedit = request.form.get('eSubtitle')
            contentedit = request.form.get('econtent')
            post.title = Titleedit
            post.Subtitle = Subtitleedit
            post.content = contentedit
            db.session.commit()
            return redirect('/post/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', value=values, post=post)



#delete the post
@app.route("/delete/<string:sno>",methods=['GET','POST'])
@login_required
def delete(sno):
    post=Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('login'))




@app.route("/profile/dashboard")
@login_required
def dashboard():
    post = Posts.query.filter_by(user_id=current_user.id)
    return render_template('dashboard.html',value=values,post=post)

#logout the user
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/login/review")
def review():
    if ('user' in session and session['user']==values['username']):
        contacts=Contact.query.filter_by().all()
        return render_template('review.html',value=values,contacts=contacts)
    return redirect(url_for('login'))


@app.route("/admin")
def optional():
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)