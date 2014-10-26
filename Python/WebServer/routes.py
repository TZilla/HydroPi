from WebServer import app,mongo
from WebServer.forms import ContactForm,RegistrationForm,SignInForm,ProfileEdit,NewListForm,EditListForm,NewEventForm,EditEventForm
from wtforms import Form,SubmitField,widgets,BooleanField,HiddenField,SelectField
from wtforms.widgets import HiddenInput
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, escape, session,send_from_directory,Markup
from werkzeug.security import generate_password_hash, check_password_hash

from time import gmtime,strftime
import os
from xml.etree import ElementTree as ET
from bson.objectid import ObjectId
from random import randint

@app.route('/lists')
def lists(): 
    #need to display all  users lists and option to search all lists
    if('username' in session):
        lists=[]
        modlist=[]
        u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
        lists = [x for x in mongo.db.lists.find({})]
        #app.logger.debug(listids.count())
        if(len(lists)!=0):
            for e in lists:
                temp=mongo.db.listmap.find_one({'l_id':e['_id'],'u_id':u_id})
                if(temp is not None):
                    e['perm']=temp['perm']
                    e['perm']=0
                modlist.append(e)
        if(len(modlist)!=0):
            return render_template('lists.html',title='All Lists',lists=modlist)
        else:
            return render_template('index.html',title='All Lists')
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))

@app.route('/events')
def events(): 
    #need to display all  users lists and option to search all lists
    if('username' in session):
        eventids=[]
        events=[]
        u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
        listids =[x for x in mongo.db.listmap.find({'u_id':u_id}) if x['perm'] > 0]
        if(len(listids)!=0):
            for l in listids:
                #[app.logger.debug('EventMap: ' + str(x)) for x in mongo.db.eventmap.find({'l_id':ObjectId(l['l_id'])})]
                eventids=[x for x in mongo.db.eventmap.find({'l_id':ObjectId(l['l_id'])})]
                if(len(eventids)!=0):
                    for e in eventids:
                        events.append(mongo.db.events.find_one({'_id':e['e_id']})) 
                            
        app.logger.debug(events)                    
        if(len(events)!=0):
            return render_template('events.html',title='My Events',events=events)
        else:
            return render_template('events.html',title='My Events')
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
    
@app.route('/viewevent/<e_id>')
def viewevent(e_id): 
    #need to display all  users lists and option to search all lists
    if('username' in session):
        if(len(e_id)==24):
            u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
            event = mongo.db.events.find_one({'_id':ObjectId(e_id)})
            eventmap=[x for x in mongo.db.eventmap.find({'e_id':ObjectId(e_id)})]
            #TODO implement event permissions
            perm=2
            lists=[]
            for e in eventmap:
                lists.append(mongo.db.lists.find_one({'_id':ObjectId(e['l_id'])}))
            app.logger.debug(lists)
                
            if(lists):
                return render_template('viewevent.html',title='View Event - ' + event['name'],lists=lists,perm=perm,e_id=e_id,event=event)
            else:
                flash('Event does not exist.','alert-danger')
                return redirect(url_for('events'))
        else:
            flash('Invalid event','alert-danger')
            return redirect(url_for('events'))
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
    
@app.route('/runevent/<e_id>')
def runevent(e_id): 
    if('username' in session):
        if(len(e_id)==24):
            u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
            event = mongo.db.events.find_one({'_id':ObjectId(e_id)})
            eventmap=[x for x in mongo.db.eventmap.find({'e_id':ObjectId(e_id)})]
            #TODO implement event permissions
            perm=2
            lists=[]
            for e in eventmap:
                lists.append(mongo.db.lists.find_one({'_id':ObjectId(e['l_id'])}))
            app.logger.debug(lists)
            elements=[]
            if(lists):
                for l in lists:
                    for e in l['elements']:
                        elements.append(e['name'])
                choice=doPicking(elements)
                flash('Item chosen: '+choice+'! (This may or may not be potato)','alert-success')
                return render_template('viewevent.html',title='View Event - ' + event['name'],lists=lists,perm=perm,e_id=e_id,event=event)
            else:
                flash('Event does not exist.','alert-danger')
                return redirect(url_for('events'))
        else:
            flash('Invalid event','alert-danger')
            return redirect(url_for('events'))
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))  

@app.route('/')
def index(): 
    #need to display all  users lists and option to search all lists
    if('username' in session):
        lists=[]
        u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
        listids =[x for x in mongo.db.listmap.find({'u_id':u_id}) if x['perm'] > 0]
        #app.logger.debug(listids.count())
        if(len(listids)!=0):
            for e in listids:
                temp=mongo.db.lists.find_one({'_id':e['l_id']})
                if(temp is not None):
                    temp['perm']=e['perm']
                    lists.append( temp )
        if(len(lists)!=0):
            return render_template('index.html',title='My lists',lists=lists)
        else:
            return render_template('index.html',title='My Lists')
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
    
def get_user_list_perm(l_id,username):
    u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
    perm=mongo.db.listmap.find_one({'l_id':ObjectId(l_id),'u_id':u_id})
    perm=0 if perm==None else perm['perm']
    return perm

@app.route('/viewlist/<l_id>')
def viewlist(l_id): 
    #need to display all  users lists and option to search all lists
    if('username' in session):
        if(len(l_id)==24):
            thelist=mongo.db.lists.find_one({'_id':ObjectId(l_id)})
            perm=get_user_list_perm(l_id, session['username'])
            #app.logger.debug(listids.count())
            if(thelist):
                return render_template('viewlist.html',title='View List - ' + thelist['name'],thelist=thelist,l_id=l_id,perm=perm)
            else:
                flash('List does not exist.','alert-danger')
                return redirect(url_for('index'))
        else:
            flash('Invalid list','alert-danger')
            return redirect(url_for('index'))
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))

@app.route('/addusers/<l_id>', methods=['GET', 'POST'])
def addusers(l_id): 
    class F(Form):
        pass
    #need to display all  users lists and option to search all lists
    if('username' in session):
        if(len(l_id)==24):
            if request.method == 'GET':
                thelist=mongo.db.lists.find_one({'_id':ObjectId(l_id)})
                listmap=mongo.db.listmap.find({'l_id':ObjectId(l_id)})
                _listmap={}
                usermap=[]
                for e in listmap:
                    _listmap[e['u_id']]=e
                    usermap.append(e['u_id'])
    
                #app.logger.debug(_listmap)
                #app.logger.debug(usermap)
                #app.logger.debug(_listmap[1]['perm'])
                #[app.logger.debug(x) for x in mongo.db.users.find({})]
    
                users=[]
                for x in mongo.db.users.find({}):
                    if(x['_id'] in usermap):
                        perm=_listmap[x['_id']]['perm']
                        setattr(F,"{}_view".format(x['_id']),BooleanField('',default=True if perm==1 or perm==3 else False))
                        setattr(F,"{}_modify".format(x['_id']),BooleanField('',default=True if perm==2 or perm==3 else False))
                        users.append([x['_id'],x['username'],perm])
                    else:
                        setattr(F,"{}_user".format(x['_id']),HiddenField('',default='{},{},{}'.format(x['_id'],x['username'],0)))
                        setattr(F,"{}_view".format(x['_id']),BooleanField('',default=False))
                        setattr(F,"{}_modify".format(x['_id']),BooleanField('',default=False))
                        users.append([x['_id'],x['username'],0])
                        
                setattr(F,"submit",SubmitField('Save'))
                if(thelist and users):
                    session['userlist'] = users
                    form=F()
                    return render_template('addusers.html',title='Add users - ' + thelist['name'],thelist=thelist,users=users,l_id=l_id,form=form)
                else:
                    flash('List does not exist.','alert-danger')
                    return redirect(url_for('index'))
            elif request.method == 'POST':
                for user in session['userlist']:
                    perm=0
                    if '{}_view'.format(user[0]) in request.form:
                        perm+=1
                    if '{}_modify'.format(user[0]) in request.form:
                        perm+=2

                    mongo.db.listmap.update({"l_id":ObjectId(l_id),"u_id":user[0]},{"$set":{'perm':perm}},upsert=True)
                session.pop('userlist',None)
                flash('List Saved successfully.', 'alert-success')
                return redirect('/viewlist/{}'.format(l_id))
            else:
                flash('Error: Invalid method')
                return redirect(url_for('index'))
        else:
            flash('Invalid list','alert-danger')
            return redirect(url_for('index'))
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))

@app.route('/newlist',methods=['GET', 'POST'])
def newlist(): 
    form=NewListForm()
    if('username' in session):
        if request.method == 'POST':
            if(form.validate()==False):
                return render_template('newlist.html',title='New List',form=form)
            else:
                #add form data to db and create the proper mappings
                date = strftime("%Y_%m_%d-%H:%M:%S",gmtime())
                u_id = mongo.db.users.find_one({'username':session['username'].lower()})['_id']
                #construct elements list
                elementlist = []
                for e in form.elements.data.split(','):
                    elementlist.append({'name':e.strip(),'rank':0,'last_picked_date':'N/A'})
                l_id = mongo.db.lists.insert({'public':form.public.data,'created_by':session['username'],'created_date':date,'modified_date':'','modified_by':'','name':form.name.data,'elements':elementlist,'description':form.description.data},safe=True)
                mongo.db.lists.update({'l_id':l_id},{'$set':{'l_id':l_id}})
                mongo.db.listmap.insert({'l_id':l_id,'u_id':u_id,'perm':2})

                flash('List created successfully', 'alert-success')
                
                return redirect(url_for('index'))
        elif request.method == 'GET':
            return render_template('newlist.html',title="New List",form=form)
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
 
@app.route('/newevent',methods=['GET', 'POST'])
def newevent(): 

    if('username' in session):
        lists=[]
        hidden=[]
        u_id=mongo.db.users.find_one({'username':session['username'].lower()})['_id']
        listids =[x for x in mongo.db.listmap.find({'u_id':u_id}) if x['perm'] > 0]
        #app.logger.debug(listids.count())
        i=0
        if(len(listids)!=0):
            for e in listids:
                temp=mongo.db.lists.find_one({'_id':e['l_id']})
                if(temp is not None):
                    lists.append( (i,"{}: {}".format(temp['name'],temp['description']) ))
                    hidden.append((i,temp['_id']))
                    i+=1
        #if(len(lists)!=0):
            #app.logger.debug(lists)
        setattr(NewEventForm,"hidden",HiddenField(''))
        setattr(NewEventForm,"list",SelectField('',coerce=int,choices=lists))
        form=NewEventForm(hidden=hidden)
        if request.method == 'POST':
            if(form.validate()==False):
                return render_template('newevent.html',title='New Event',form=form)
            else:
                #add form data to db and create the proper mappings
                date = strftime("%Y_%m_%d-%H:%M:%S",gmtime())
                e_id = mongo.db.events.insert({'created_by':session['username'],'created_date':date,'modified_date':'','modified_by':'','name':form.name.data,'description':form.description.data},safe=True)
                mongo.db.eventmap.insert({'e_id':e_id,'l_id':eval(form.hidden.data)[form.list.choices[form.list.data][0]][1]})
                
                flash('Event created successfully', 'alert-success')
                return redirect(url_for('events'))
        elif request.method == 'GET':
                return render_template('newevent.html',title='New Event',form=form)
        else:
            return render_template('newevent.html',title='New Event')
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
   
@app.route('/editlist/<l_id>',methods=['GET', 'POST'])
def editlist(l_id): 
    form=EditListForm()
    #need to display all  users lists and option to search all lists
    if('username' in session):
        perm=get_user_list_perm(l_id, session['username'])
        if perm != 2 and perm != 3:
            flash('Insufficient permissions to edit list.','alert-danger')
            return redirect('/viewlist/{}'.format(l_id))
        if request.method == 'POST':
            if(len(l_id)==24):
                if(form.validate()==False):
                    return render_template('editlist.html',title='New List',form=form,l_id=l_id)
                else:
                    elementlist=[]
                    for e in form.elements.data.split(','):
                        elementlist.append({'name':e.strip(),'rank':0,'last_picked_date':'N/A'})
                    date = strftime("%Y_%m_%d-%H:%M:%S",gmtime())
                    mongo.db.lists.update({'_id':ObjectId(l_id)},{'$set':{"name":form.name.data,"description":form.description.data,'elements':elementlist,'modified_date':date,'modified_by':session['username'],'public':form.public.data}})
                    flash('List updated successfully','alert-success')
                    return redirect('/viewlist/'+l_id)
            else:
                flash('Invalid list','alert-danger')
                return redirect(url_for('index'))
        elif request.method == 'GET':
            if(len(l_id)==24):
                thelist=mongo.db.lists.find_one({'_id':ObjectId(l_id)})
                app.logger.debug(thelist)
                if(thelist):
                    form.description.data=thelist['description']
                    form.name.data=thelist['name']
                    form.public.data=thelist['public']
                    elemstr=''
                    for e in thelist['elements']:
                        elemstr=elemstr+e['name']+','
                    elemstr=elemstr[:-1]
                    form.elements.data=elemstr    
                    return render_template('editlist.html',title="Edit List - " + thelist['name'],form=form,l_id=l_id)
                else:
                    flash('List does not exist.','alert-danger')
                    return redirect(url_for('index'))
            else:
                flash('Invalid list','alert-danger')
                return redirect(url_for('index'))
            
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))
    
@app.route('/editevent/<e_id>',methods=['GET', 'POST'])
def editevent(e_id): 
    flash('Editing of events is currently disabled, Sorry!','alert-warning')
    return redirect('/viewevent/'+e_id)
    form=EditEventForm()
    #need to display all  users lists and option to search all lists
    if('username' in session):
        perm=get_user_list_perm(l_id, session['username'])
        if perm != 2 and perm != 3:
            flash('Insufficient permissions to edit list.','alert-danger')
            return redirect('/viewlist/{}'.format(l_id))
        if request.method == 'POST':
            if(len(l_id)==24):
                if(form.validate()==False):
                    return render_template('editlist.html',title='New List',form=form,l_id=l_id)
                else:
                    elementlist=[]
                    for e in form.elements.data.split(','):
                        elementlist.append({'name':e.strip(),'rank':0,'last_picked_date':'N/A'})
                    date = strftime("%Y_%m_%d-%H:%M:%S",gmtime())
                    mongo.db.lists.update({'_id':ObjectId(l_id)},{'$set':{"name":form.name.data,"description":form.description.data,'elements':elementlist,'modified_date':date,'modified_by':session['username'],'public':form.public.data}})
                    flash('List updated successfully','alert-success')
                    return redirect('/viewlist/'+l_id)
            else:
                flash('Invalid list','alert-danger')
                return redirect(url_for('index'))
        elif request.method == 'GET':
            if(len(l_id)==24):
                thelist=mongo.db.lists.find_one({'_id':ObjectId(l_id)})
                app.logger.debug(thelist)
                if(thelist):
                    form.description.data=thelist['description']
                    form.name.data=thelist['name']
                    form.public.data=thelist['public']
                    elemstr=''
                    for e in thelist['elements']:
                        elemstr=elemstr+e['name']+','
                    elemstr=elemstr[:-1]
                    form.elements.data=elemstr    
                    return render_template('editlist.html',title="Edit List - " + thelist['name'],form=form,l_id=l_id)
                else:
                    flash('List does not exist.','alert-danger')
                    return redirect(url_for('index'))
            else:
                flash('Invalid list','alert-danger')
                return redirect(url_for('index'))
            
    else:
        flash('Not signed in.','alert-danger')
        return redirect(url_for('signin'))


@app.route('/clear')
def cleardb():
    
    mongo.db.users.remove({})
    mongo.db.counters.remove({})
    mongo.db.counters.insert({
      '_id': "userid",
      'seq': 0
   })
   
    mongo.db.lists.remove({})
    mongo.db.listmap.remove({})
    mongo.db.events.remove({})
    mongo.db.eventmap.remove({})
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html',title="About")
 
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('contact.html', form=form,title="Contact")
        else:
            flash('Thank you for your message. We\'ll get back to you shortly.','alert-success')
            return render_template('contact.html', form=form, title="Contact")
 
    elif request.method == 'GET':
        return render_template('contact.html', form=form,title="Contact")
    
@app.route('/register',methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form1 = SignInForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form,title="Register New User")
        else:
            add_user(form.username.data,form.firstname.data,form.lastname.data,form.email.data,form.password.data,form.salt)
            flash('User ' + form.username.data + ' registered successfully, please sign in.','alert-success' )
            return render_template('signin.html', title="Sign in",form=form1)
    elif request.method == 'GET':
        return render_template('register.html', form=form,title="Register New User")

@app.route('/signin',methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if('username' in session.keys()):
        flash('User ' + session['username'] + ' already signed in.','alert-success' )
        return redirect(url_for('index'))
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form,title="Sign in")
        else:
            session['username']=form.username.data
            flash('User ' + session['username'] + ' signed in successfully.','alert-success' )
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('signin.html', form=form,title="Sign in")
    
@app.route('/signout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    flash('Signed out successfully.', 'alert-success')
    return redirect(url_for('index'))  

@app.route('/user/<name>')
def profile(name):
    form=ProfileEdit()

    # remove the username from the session if it's there
    user = mongo.db.users.find_one({'username':name.lower()})
    if('username' in session):
        if(user is not None):
            if(session['username'].lower() == name.lower()):
                app.logger.debug('user can edit')
                return render_template('profile.html', name=name, username=user['username'],firstname=user['firstname'],lastname=user['lastname'],email=user['email'],joindate=user['joindate'],title="Profile",profileimg=user['img'],form=form)
            else:    
                return render_template('profile.html', name=name, username=user['username'],firstname=user['firstname'],lastname=user['lastname'],email=user['email'],joindate=user['joindate'],title="Profile",profileimg=user['img'])
        else:
            return render_template('profile.html', name='missing',title="Profile")
    else:
        return render_template('profile.html', name='offline',title="Profile")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')        
def doPicking(list):
    sel = randint(0,len(list)-1)
    item=list[sel]
    return item
def add_user(username,firstname,lastname,email,password,salt):
    #insert user
    date = strftime("%Y_%m_%d",gmtime())
    mongo.db.users.insert({'img':"",'salt':salt,'_id':getNextSequence('userid'),'username':username.lower(),'firstname':firstname,'lastname':lastname,'password':password,'email':email.lower(),'status':'OFFLINE','joindate':date})
    
def getNextSequence(name):
    ret=mongo.db.counters.find_and_modify(query= { '_id': name },update={ '$inc': { 'seq': 1 } },new= True)
    print(ret)
    return ret['seq']
