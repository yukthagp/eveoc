import os
#import pytz
from flask import Flask,flash, render_template, request, redirect,send_from_directory,url_for,session  # ,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date,time
from passlib.hash import sha256_crypt
#from flask_uploads import UploadSet, IMAGES, configure_uploads, ALL
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import SubmitField
import smtplib
import random
#from werkzeug.utils import secure_filename, FileStorage
import bcrypt
#from flask_security import Security, SQLAlchemySessionUserDatastore#, SQLAlchemyUserDatastore

#import os
#basedir = os.path.abspath(os.path.dirname(__file__))
#IST = pytz.timezone('Asia/Kolkata')
current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    current_dir, "database.db")
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = './static/images/'
app.config['SECRET_KEY'] = 'theszrandodxghdcgncmstring' #Read this from OS env in case of production
#app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
#app.config['SECURITY_PASSWORD_SALT'] = 'thisshouldbeasuperstrongsalt217dn' #Read this from OS env in case of production
#app.config['SECURITY_REGISTERABLE'] = True #So that we can register new user and they can login
#app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
#app.config['SECURITY_UNAUTHORIZED_VIEW'] = None #THROWS 403 WHEN NOT AUTHORISED- if "None" is specified default page will be shown



#photos= UploadSet('photos',IMAGES)
#configure_uploads(app,photos)
db = SQLAlchemy()
db.init_app(app)

#user_datastore= SQLAlchemySessionUserDatastore(db.session,User,Role)
#security=Security(app,user_datastore)
app.app_context().push()


#Models

class Customer(db.Model):
  __tablename__ = 'customer'
  customer_ID = db.Column(db.Integer, autoincrement=True, primary_key=True)
  customer_name = db.Column(db.String, nullable=True)
  customer_logged_in = db.Column(db.Boolean, nullable=True)
  customer_phone_no = db.Column(db.Integer, nullable=True)
  customer_address = db.Column(db.String, nullable=True)
  # make sure one mail can sign up only once
  customer_email = db.Column(db.String, unique=True, nullable=True)
  customer_password = db.Column(db.String, nullable=True)

class Events(db.Model):
   __tablename__='events'
   events_ID=db.Column(db.Integer, autoincrement=True, primary_key=True)
   event_name=db.Column(db.String, nullable=False)
   event_category=db.Column(db.String, nullable=False)
   #event_sub_category=db.Column(db.String, nullable=False)
   event_no_of_days=db.Column(db.Integer,nullable=False)#days
   event_no_of_organisers=db.Column(db.Integer,nullable=False)#mic
   event_no_of_people=db.Column(db.Integer, nullable=False)#tickets
   #total events in place of flag


class Organiser(db.Model):
   __tablename__='organiser'
   organiser_ID=db.Column(db.Integer, autoincrement=True, primary_key=True)
   organiser_name=db.Column(db.String, nullable=True)
   organiser_ratings=db.Column(db.Integer,nullable=True)
   organiser_about=db.Column(db.String, nullable=True)
   organiser_feature_image=db.Column(db.String,nullable=True)
   #organiser_event_name=db.Column(db.String,nullable=False) one organiser can have many events

class Category(db.Model):
   __tablename__='category'
   category_ID=db.Column(db.Integer, autoincrement=True, primary_key=True)
   events_ID = db.Column(db.ForeignKey("events.events_ID"), nullable=True)
   category_name=db.Column(db.String, nullable=True)
   organiser_ID=db.Column(db.ForeignKey("organiser.organiser_ID"), nullable=True)
   category_quoted_price=db.Column(db.String,nullable=True)
   category_event_description=db.Column(db.String,nullable=True)
   category_event_features=db.Column(db.String,nullable=True)
   category_not_available_features=db.Column(db.String,nullable=True)
   category_image=db.Column(db.String,nullable=True)


class Bookings(db.Model):
   __tablename__='bookings'
   booking_ID=db.Column(db.Integer, autoincrement=True, primary_key=True)
   booking_for_date=db.Column(db.Date, nullable=False)
   booking_start_time=db.Column(db.Time,nullable=False)
   booking_end_time=db.Column(db.Time,nullable=False)
   booked_on_date=db.Column(db.Date,nullable=False)
   booked_on_time=db.Column(db.Time,nullable=False)
   category_ID = db.Column(db.ForeignKey("category.category_ID"), nullable=False)
   customer_ID = db.Column(db.ForeignKey("customer.customer_ID"), nullable=False)
   booking_status=db.Column(db.String,nullable=False)
   booking_message=db.Column(db.String,nullable=True)

class Schedule(db.Model):
   __tablename__='schedule'
   schedule_ID=db.Column(db.Integer, autoincrement=True, primary_key=True)
   booking_ID = db.Column(db.ForeignKey("bookings.booking_ID"), nullable=False)
   schedule_start_time=db.Column(db.Time,nullable=False)
   schedule_end_time=db.Column(db.Time,nullable=False)
   schedule_start_date=db.Column(db.Date,nullable=False)
   schedule_end_date=db.Column(db.Date,nullable=False)
   schedule_split_time=db.Column(db.String,nullable=False)
   schedule_titles=db.Column(db.String,nullable=False)
   schedule_venues=db.Column(db.String,nullable=False)


#db.create_all()

"""new_cust=Customer(customer_email="yuktha142002@gmail.com",
                  customer_name="Yuktha",
                  customer_phone_no=9008095986,
                  customer_address="#141, 1st C Main Road, Domlur, 5600071",
                  customer_password=sha256_crypt.hash("abcd"),
                  customer_logged_in=False)
db.session.add(new_cust)
db.session.commit()
new_category=Category(events_ID=1,
                  category_name="Birthday",
                  organiser_ID=1,
                  category_quoted_price=5000,
                  category_event_description="Birthdays are what need to be celebrated",
                  category_event_features="Catering,AC,Separate space",
                  category_not_available_features="Travel arrangement,Complimentary Juice",
                  category_image="7_delights.webp"
                  )
db.session.add(new_category)
db.session.commit()"""

@app.route("/", methods=["GET", "POST"])
def guesthome():
    if request.method == "GET":
        organiser_objs=Organiser.query.all()
        events=Events.query.all()
        days=0
        organisers=len(Organiser.query.all())
        people=0
        category=len(Category.query.all())
        for obj in events:
           people+=obj.event_no_of_people*obj.event_no_of_organisers
           days+=obj.event_no_of_days
           
        featured_images=["birthday1.jpg",'birthday2.jpg','Concert3.jpg','Concert5.jpg','gallery-full-six.jpg','Meeting 1.jpg']
        return render_template("guest_home.html", customer_email="GUEST", customer_logged_in=False,organiser_objs=organiser_objs,featured_images=featured_images,
                               days=days,organisers=organisers,category=category,people=people)#, all_cust_emails=all_cust_emails
    else:
        return redirect("/login_required")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", customer_email="GUEST", customer_logged_in=False)#, all_cust_emails=all_cust_emails
    else:
        customer_email = request.form['customer_email']
        customer_password = request.form['customer_password']
        customer_logged = db.session.query(Customer).filter(
        Customer.customer_email == customer_email).first()
        if customer_logged:
            if (sha256_crypt.verify(customer_password,
                                    customer_logged.customer_password)):
                customer_logged.customer_logged_in = True
                db.session.commit()
                # customer_activity=customer_logged.customer_logged_in
                url = "/home/" + str(customer_logged.customer_email)
                return redirect(url)
            else:
                return render_template('incorrect_pw.html',
                                    customer_email=customer_email,
                                    has_purchased=False)
        else:
            return render_template('email_DNE.html',
                                    customer_email=customer_email,
                                    has_purchased=False)
    


@app.route("/home/<string:customer_email>", methods=["GET", "POST"])
def home(customer_email):
  if request.method == "GET":
    organiser_objs=Organiser.query.all()
    events=Events.query.all()
    days=0
    organisers=len(Organiser.query.all())
    people=0
    category=len(Category.query.all())
    for obj in events:
        people+=obj.event_no_of_people*obj.event_no_of_organisers
        days+=obj.event_no_of_days
    #featured = Stock.query.filter_by(stock_type="Featured").all()
    all_cust_objs = Customer.query.all()
    all_cust_emails = []
    for i in all_cust_objs:
      all_cust_emails += [i.customer_email]
    cust_obj = Customer.query.filter_by(customer_email=customer_email).first()
    organiser_objs=Organiser.query.all()
    if cust_obj is not None:
      logged_in = cust_obj.customer_logged_in
      if logged_in:
        featured_images=["birthday1.jpg",'birthday2.jpg','Concert3.jpg','Concert5.jpg','gallery-full-six.jpg','Meeting 1.jpg']
        return render_template("homepage.html",
                               customer_email=customer_email,
                               all_cust_emails=all_cust_emails,
                               customer_logged_in=logged_in,
                               organiser_objs=organiser_objs,
                               featured_images=featured_images,
                               days=days,organisers=organisers,category=category,people=people)
      else:
        return redirect("/")
    else:
      logged_in = False
      return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
  if request.method == 'GET':
    customer_email = "GUEST"
    return render_template("signup.html",
                           customer_email=customer_email,
                           has_purchased=False)
  else:
    customer_email = request.form['customer_email']
    otp=random.randint(10000,99999)

    FROM = 'yuktha142002@gmail.com'
    TO = customer_email if isinstance(customer_email,
                                      list) else [customer_email]
    SUBJECT = 'Confirm your Registration | Eveoc'
    TEXT = """Greetings from Eveoc,\n Use the otp provided below to confirm your registration\n""" + str(otp)

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
      server = smtplib.SMTP("smtp.gmail.com", 587)
      server.ehlo()
      server.starttls()
      server.login('yuktha142002@gmail.com', 'lbnv wqjk ekfk afnl')
      server.sendmail(FROM, TO, message)
      server.close()
      print('successfully sent the mail')
    except:
      print("failed to send mail")
      return render_template("mail_failed.html")
    customer_add1 = "t"
    customer_add2 = request.form['customer_add2']
    customer_pincode = request.form['customer_pincode']

    session["cust_dict"]={"customer_password" : sha256_crypt.hash(request.form['customer_password']),
    "customer_phno" : request.form['customer_phno'],
    "customer_email":request.form['customer_email'],
    "customer_add1" : request.form['customer_add1'],
    "customer_add2" : request.form['customer_add2'],
    "customer_pincode" : request.form['customer_pincode'],
    "otp":otp,
    "customer_name":request.form['customer_name'],
    "customer_address" : customer_add1 +"\n"+ customer_add2 + ", " + customer_pincode}
    return redirect(url_for("sign_up_validate",customer_email=customer_email))
  
@app.route("/signup/validate/<string:customer_email>", methods=["GET", "POST"])
def sign_up_validate(customer_email):
    #cust_dict=request.args.get(cust_dict)
    #print(cust_dict)
    cust_dict=session["cust_dict"]
    print(cust_dict)
    if request.method=="GET":
       return render_template("signup_otp.html")
    else:
      #cust_dict=inputt
      new_customer_email=cust_dict['customer_email']
      #print(cust_email)
      customer_password=cust_dict["customer_password"]
      customer_phno=cust_dict["customer_phno"]
      new_customer_email=cust_dict["customer_email"]
      customer_name=cust_dict["customer_name"]
      customer_address=cust_dict["customer_address"]
      customer_otp=cust_dict["otp"]
      entered_otp=int(request.form["otp"])
      if customer_otp!=entered_otp:
        return render_template("Wrong_otp.html",customer_email=customer_email)
      existing_customer = db.session.query(Customer).filter(
        Customer.customer_email == new_customer_email).first()
      if existing_customer is not None:
        return render_template('email_exists.html', has_purchased=False)
      else:
        #new_customer_email = request.form['customer_email']
        #new_customer_name = request.form['customer_name']
        new_customer = db.session.query(Customer).filter(
          Customer.customer_email == new_customer_email).first()
        if new_customer is not None:
          return render_template('email_exists.html', has_purchased=False)
        else:
          new_customer = Customer(customer_email=new_customer_email,
                                  customer_name=customer_name,
                                  customer_password=customer_password,
                                  customer_phone_no=customer_phno,
                                  customer_address=customer_address,
                                  customer_logged_in=True)
          db.session.add(new_customer)
          db.session.commit()
          url = "/home/" + str(new_customer_email)
          return redirect(url)

"""@app.route("/home/official_event/<string:customer_email>", methods=["GET", "POST"])
def official(customer_email):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
          return render_template("services.html",customer_email=customer_email)
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")"""

@app.route("/home/<string:customer_email>/my_events", methods=["GET", "POST"])
def my_events(customer_email):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
          my_events_objs=Bookings.query.filter_by(customer_ID=cust_obj.customer_ID).all()
          #events_obj=Events.query.filter_by(event_category=event_category).first()
          bookings=[]
          for bobj in my_events_objs:
             cat_obj=Category.query.get(bobj.category_ID)
             cat_image=cat_obj.category_image
             month=["Zero","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
             event_obj=Events.query.filter_by(event_category=cat_obj.category_name).first()
             dictt={"Booking ID":bobj.booking_ID,"Event Date":bobj.booking_for_date,"Event Time":bobj.booking_start_time,
                    "Booked on": bobj.booked_on_date,"Booking Status": bobj.booking_status,"Category Image": cat_image,
                    "Event Category": event_obj.event_category,"Booked Event":event_obj.event_category,"Only date":str(bobj.booking_for_date)[8:],"Only month":month[int(str(bobj.booking_for_date)[5:7])]}
             bookings.append(dictt)
             
          #category_obj=Category.query.get(category_ID)
          #cat_image=category_obj.category_image
          #print(bookings)
          return render_template("my_events.html",customer_email=customer_email,customer_logged_in=cust_obj.customer_logged_in,
                                 my_events_objs=my_events_objs,bookings=bookings)#after booking, redirect to schedule.html
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")

@app.route("/home/services/<string:event_category>/<string:customer_email>", methods=["GET", "POST"])
def services(event_category,customer_email):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
        events_obj=Events.query.filter_by(event_category=event_category).first()
        events_ID=events_obj.events_ID
        category_objs=Category.query.filter_by(events_ID=events_ID).all()
        cat_objs=[]
        """cat_obj={organiser_name:None, category_quoted_price:None,category_event_description:None,
                  category_event_features:None,category_not_available_features:None,category_image:None}"""
        for obj in category_objs:
            
            organiser_ID=obj.organiser_ID
            organiser_obj=Organiser.query.get(organiser_ID)
            organiser_name=organiser_obj.organiser_name
            if obj.category_event_features and obj.category_not_available_features:
              obj_avail_f=(obj.category_event_features).split(",")
              obj_not_avail_f=(obj.category_not_available_features).split(",")
            elif obj.category_event_features:
               obj_avail_f=(obj.category_event_features).split(",")
               obj_not_avail_f=[]
            elif obj.category_not_available_features:
               obj_not_avail_f=(obj.category_not_available_features).split(",")
               obj_avail_f=[]
            else:
               obj_avail_f=[]
               obj_not_avail_f=[]
            cat_obj={"organiser_name":organiser_name, "category_quoted_price":obj.category_quoted_price,
                      "category_event_description":obj.category_event_description,
                    "category_event_features":obj_avail_f,
                    "category_not_available_features":obj_not_avail_f,
                    "category_image":obj.category_image,"category_ID":obj.category_ID}
               
            
            """category_quoted_price=obj.organiser_quoted_price
            category_event_description=obj.category_event_description
            category_event_features=(obj.category_event_features).split(",")
            category_not_available_features=(obj.category_not_available_features).split(",")
            category_image=obj.category_image"""
            cat_objs.append(cat_obj)
            #print(cat_objs)
        return render_template("services.html",customer_email=customer_email,customer_logged_in=cust_obj.customer_logged_in,event_category=event_category,cat_objs=cat_objs,events_obj=events_obj)
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")
    
@app.route("/home/services/<string:event_category>/<string:customer_email>/book_event/<int:category_ID>", methods=["GET", "POST"])
def book_event(event_category,customer_email,category_ID):
  all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
  emails=[]
  for obj in all_cust_objs:
    emails+=[obj.customer_email]
  if (customer_email in emails):
    cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
  else:
     return redirect("/login_required")
  if request.method == 'GET':
       category_obj=Category.query.get(category_ID)
       organiser_obj=Organiser.query.get(category_obj.organiser_ID)
       events_obj=Events.query.filter_by(event_category=event_category).first()
             
          #category_obj=Category.query.get(category_ID)
          #cat_image=category_obj.category_image
       if cust_obj.customer_logged_in:
          #print(bookings)
          return render_template("booking_details.html",customer_email=customer_email,customer_logged_in=cust_obj.customer_logged_in,event_category=event_category,
                                 category_obj=category_obj,events_obj=events_obj,organiser_obj=organiser_obj)
       else:
          return redirect("/login_required")
  else:
     if cust_obj.customer_logged_in:
        book_date=request.form["date"]
        book_from_time=request.form["time1"]
        book_till_time=request.form["time2"]

        datee =str(datetime.now()).split(" ")[0]
        day = int(datee[8:10])
        month = int(datee[5:7])
        year = int(datee[0:4])
        timee = str(datetime.now()).split(" ")[1][0:8]
        hh = int(timee[0:2])
        mm = int(timee[3:5])
        ss = int(timee[6:8])
        boyy,bomm,bodd=tuple([int(i) for i in book_date.split("-")])
        bfhh,bfmm=tuple([int(i) for i in book_from_time.split(":")])
        bthh,btmm=tuple([int(i) for i in book_till_time.split(":")])

        booking_for_date=date(boyy,bomm,bodd)
        booking_start_time=time(bfhh,bfmm)
        booking_end_time=time(bthh,btmm)
        booking_message=request.form["message"]
        customer_ID=cust_obj.customer_ID
        new_booking = Bookings(booking_for_date=booking_for_date,
                                booking_start_time=booking_start_time,
                                booking_end_time=booking_end_time,
                                booked_on_date=date(year,month,day),
                                booked_on_time=time(hh,mm,ss),
                                category_ID=category_ID,
                                customer_ID=customer_ID,
                                booking_status="SENT",
                                booking_message=booking_message
                                )
        db.session.add(new_booking)
        db.session.commit()
        obj_last=Bookings.query.all()[-1]
        booking_obj=Bookings.query.get(obj_last.booking_ID)
        category_obj=Category.query.get(category_ID)

        cat_image=category_obj.category_image
        #bookings=[]
        #if cust_obj.customer_logged_in:
          #for bobj in events_obj:
             #cat_obj=Category.query.get(bobj.category_ID)
             #cat_image=cat_obj.category_image
             #dictt={"Booking ID":bobj.booking_ID,"Event Date":bobj.booking_for_date,"Event Time":bobj.booking_start_time,"Booked on": bobj.booked_on_date,"Booking Status": bobj.booking_status,"Category Image": cat_image}
             #bookings.append(dictt)
        return render_template("booking_success.html",customer_email=customer_email,
                               customer_logged_in=cust_obj.customer_logged_in,booking_obj=booking_obj,
                               category_ID=category_ID,category_obj=category_obj)

@app.route("/home/gallery/<string:customer_email>", methods=["GET", "POST"])
def gallery(customer_email):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
          return render_template("gallery.html",customer_email=customer_email,customer_logged_in=cust_obj.customer_logged_in)
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")

@app.route("/<string:customer_email>/booked_event/update/<string:event_category>/<int:booking_ID>", methods=["GET", "POST"])
def update_booking(customer_email,event_category,booking_ID):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
          booking_obj=Bookings.query.get(booking_ID)
          cat_obj=Category.query.get(booking_obj.category_ID)
          event_obj=Events.query.get(cat_obj.events_ID)
          date=str(booking_obj.booking_for_date)
          st_time=str(booking_obj.booking_start_time)
          end_time=str(booking_obj.booking_end_time)
          details=booking_obj.booking_message
          print(booking_obj.booking_message)
          #events_obj=Events.query.filter_by(event_category=event_category).first()
          
          return render_template("update_booking.html",customer_email=customer_email,customer_logged_in=cust_obj.customer_logged_in,
                                 event_category=event_obj.event_category,date=date,st_time=st_time,end_time=end_time,details=details)#after booking, redirect to schedule.html
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")
  else: 
        booking_obj=Bookings.query.get(booking_ID)
        cat_obj=Category.query.get(booking_obj.category_ID)
        category_ID=cat_obj.category_ID
        book_date=request.form["date"]
        book_from_time=request.form["time1"]
        book_till_time=request.form["time2"]
        message=request.form["message"]
        print("++++++++++++++++++++++++++++++++++++++++++++++++")
        print(book_from_time.split(":"),book_till_time.split(":"))
        if book_date:
          (boyy,bomm,bodd)=tuple([int(i) for i in book_date.split("-")])
          booking_for_date= date(boyy,bomm,bodd)
          booking_obj.booking_for_date=booking_for_date
        try:
          if book_from_time:
            (bfhh,bfmm)=tuple([int(i) for i in book_from_time.split(":")])
            booking_start_time= time(bfhh,bfmm)
            booking_obj.booking_start_time=booking_start_time
          if book_till_time:
            (bthh,btmm)=tuple([int(i) for i in book_till_time.split(":")])
            booking_end_time= time(bthh,btmm)
            booking_obj.booking_end_time=booking_end_time
        except:
           pass
        if message:
           booking_obj.booking_message=message
        db.session.commit()
        return redirect(url_for("my_events",customer_email=customer_email))
  
@app.route("/<string:customer_email>/booked_event/delete/<string:event_category>/<int:booking_ID>", methods=["GET", "POST"])
def delete_booking(customer_email,event_category,booking_ID):
  if request.method == 'GET':
    all_cust_objs=Customer.query.filter_by(customer_email=customer_email).all()
    emails=[]
    for obj in all_cust_objs:
       emails+=[obj.customer_email]
    if (customer_email in emails):
       cust_obj=Customer.query.filter_by(customer_email=customer_email).first()
       if cust_obj.customer_logged_in:
          booking_obj=Bookings.query.get(booking_ID)
          db.session.delete(booking_obj)
          db.session.commit()
          return redirect(url_for("my_events",customer_email=customer_email))
       else:
          return redirect("/login_required")
    else:
      return redirect("/login_required")
  else: 
        booking_obj=Bookings.query.get(booking_ID)
        cat_obj=Category.query.get(booking_obj.category_ID)
        category_ID=cat_obj.category_ID
        book_date=request.form["date"]
        book_from_time=request.form["time1"]
        book_till_time=request.form["time2"]
        message=request.form["message"]
        print("++++++++++++++++++++++++++++++++++++++++++++++++")
        print(book_from_time.split(":"),book_till_time.split(":"))
        if book_date:
          (boyy,bomm,bodd)=tuple([int(i) for i in book_date.split("-")])
          booking_for_date= date(boyy,bomm,bodd)
          booking_obj.booking_for_date=booking_for_date
        try:
          if book_from_time:
            (bfhh,bfmm)=tuple([int(i) for i in book_from_time.split(":")])
            booking_start_time= time(bfhh,bfmm)
            booking_obj.booking_start_time=booking_start_time
          if book_till_time:
            (bthh,btmm)=tuple([int(i) for i in book_till_time.split(":")])
            booking_end_time= time(bthh,btmm)
            booking_obj.booking_end_time=booking_end_time
        except:
           pass
        if message:
           booking_obj.booking_message=message
        db.session.commit()
        return redirect(url_for("my_events",customer_email=customer_email))
     
     

@app.route("/logout/<string:customer_email>", methods=["GET", "POST"])
def logout(customer_email):
  if request.method == 'GET':
    cust_obj = Customer.query.filter_by(customer_email=customer_email).first()
    cust_obj.customer_logged_in = False
    db.session.commit()
    return redirect("/login")

@app.route("/login_required", methods=["GET", "POST"])
def login_required():
    if request.method == "GET":
        return render_template("login_required.html")#, has_purchased=False)
    else:
        return redirect("/login")
    

    
if __name__ == '__main__':
    app.run()  # host='0.0.0.0'
