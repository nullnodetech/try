from flask import Flask,session, render_template,request,redirect, url_for
app = Flask(__name__)
app.secret_key = '23826b72637tskx86'
import sqlite3
import base64

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/',methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select * from users WHERE email=? AND password=?",(email,password))
        rows = cur.fetchall()
        if len(rows) > 0:
            for row in rows:
                session['id']=row['id']
                session['name']=row['name']
                session['user']='user'
            return redirect("/home")
        else:
            return redirect("/?err=Email or Password is Wrong!")
    else:
        return render_template('index.html')

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect("database.db")
        conn.execute('INSERT INTO users(name,email,password)VALUES(?,?,?)',(name,email,password))
        conn.commit()
        return redirect("/?msg=Signup Successfully!")
    else:
        return render_template('signup.html')

@app.route('/home')
def Home():
    if 'user' in session and session['user']=='user':
        userid=str(session['id'])
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * FROM files where user=?",(userid))
        files = cur.fetchall()
        return render_template('user/home.html',files=len(files),user=session['name'])
    else:
        return redirect('/?err=Illegal Access')

@app.route('/files')
def Files():
    if 'user' in session and session['user']=='user':
        userid=str(session['id'])
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * FROM files where user=?",(userid))
        files = cur.fetchall()
        return render_template('user/files.html',files=files,user=session['name'])
    else:
        return redirect('/?err=Illegal Access')

@app.route('/files/view')
def FilesView():
    attid = request.args.get('id') 
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * FROM files where id=?",(attid))
    file = cur.fetchall()
    return render_template('password.html',file=file[0])

@app.route('/files/open',methods = ['POST', 'GET'])
def FilesOpen():
    if request.method == 'POST':
        fileid = request.form['id']
        password = request.form['password']
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select * from files WHERE id=? AND password=?",(fileid,password))
        file = cur.fetchall()
        if len(file) > 0:
            return render_template('file.html',type=file[0]['type'],file=file[0]['data'].decode())
        else:
            return redirect("/files/view?err=File Password is Wrong!&id="+fileid)
    else:
        return render_template('index.html')

@app.route('/files/add',methods = ['POST', 'GET'])
def FileAdd():
    if request.method == 'POST':
        user=str(session['id'])
        title = request.form['title']
        password = request.form['password']
        file = request.files['file']
        data = base64.b64encode(file.read())
        conn = sqlite3.connect("database.db")
        conn.execute('INSERT INTO files(title,data,password,user,type)VALUES(?,?,?,?,?)',(title,data,password,user,file.content_type))
        conn.commit()
        conn = sqlite3.connect("database1.db")
        conn.execute('INSERT INTO files(title,data,password,user,type)VALUES(?,?,?,?,?)',(title,data,password,user,file.content_type))
        conn.commit()
        conn = sqlite3.connect("database2.db")
        conn.execute('INSERT INTO files(title,data,password,user,type)VALUES(?,?,?,?,?)',(title,data,password,user,file.content_type))
        conn.commit()
        return redirect("/files?msg=File Uploaded Successfully!")   
    else:
        return redirect("/err=Illegal Access")

@app.route('/files/delete')
def FilesDelete():
    if 'user' in session and session['user']=='user':
        attid = request.args.get('id') 
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        conn = sqlite3.connect('database1.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        conn = sqlite3.connect('database2.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        return redirect('/files?msg=File Deleted Successfully!') 
    else:
        return redirect('/?err=Illegal Access')

@app.route('/profile')
def Profile():
    if 'user' in session and session['user']=='user':
        userid=str(session['id'])
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from users WHERE id=?",(userid))
        rows = cur.fetchall()
        return render_template('user/profile.html',rows=rows[0],user=session['name'])
    else:
        return redirect('/?err=Illegal Access')

@app.route('/profile/update',methods = ['POST', 'GET'])
def ProfileUpdate():
    if request.method=='POST':
        if 'user' in session and session['user']=='user':
            userid=str(session['id'])
            oldPassword = request.form['oldPassword']
            newPassword = request.form['newPassword']
            conn = sqlite3.connect("database.db")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("select * from users WHERE id=? AND password=?",(userid,oldPassword))
            rows = cur.fetchall()
            if len(rows)>0:
                conn.execute('UPDATE users SET password=? WHERE id=?',(newPassword,userid))
                conn.commit()
                conn.close()
                return redirect('/profile?msg=Password Changed Successfully!') 
            else:
                return redirect('/profile?msg=Old Password is Wrong!') 
        else:
            return redirect('/?err=Illegal Access')
    else:
        return redirect('/?err=Illegal Access')


# 
# 
# 
# 
# 
# Admin
@app.route('/admin',methods = ['POST', 'GET'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email=='admin@gmail.com' and password=='admin':
            session['admin']='admin'
            return redirect("/admin/home")
        else:
            return redirect("/admin?err=Email or Password is Wrong!")
    else:
        return render_template('admin.html')

@app.route('/admin/home')
def adminHome():
    if 'admin' in session and session['admin']=='admin':
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * FROM users")
        users = cur.fetchall()
        cur.execute("select * FROM files")
        files = cur.fetchall()
        return render_template('admin/home.html',users=len(users),files=len(files))
    else:
        return redirect('/admin?err=Illegal Access')

@app.route('/admin/users')
def adminUsers():
    if 'admin' in session and session['admin']=='admin':
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall()
        return render_template('admin/users.html',users=users)
    else:
        return redirect('/admin?err=Illegal Access')

@app.route('/admin/users/delete')
def adminUsersDelete():
    if 'admin' in session and session['admin']=='admin':
        attid = request.args.get('id') 
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM users WHERE id=?',(attid))
        conn.commit()
        return redirect('/admin/users?msg=Users Deleted Successfully!') 
    else:
        return redirect('/admin?err=Illegal Access')

@app.route('/admin/files')
def adminFiles():
    if 'admin' in session and session['admin']=='admin':
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from files JOIN users ON users.id=files.user")
        files = cur.fetchall()
        return render_template('admin/files.html',files=files)
    else:
        return redirect('/admin?err=Illegal Access')

@app.route('/admin/files/delete')
def adminFilesDelete():
    if 'admin' in session and session['admin']=='admin':
        attid = request.args.get('id') 
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        conn = sqlite3.connect('database1.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        conn = sqlite3.connect('database2.db')
        conn.execute('DELETE FROM files WHERE id=?',(attid))
        conn.commit()
        return redirect('/admin/files?msg=File Deleted Successfully!') 
    else:
        return redirect('/admin?err=Illegal Access')

# DB
@app.route('/db')
def db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT,password TEXT,created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE files(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,data TEXT,type TEXT,password TEXT,user INTEGER,created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    conn.close()
    conn = sqlite3.connect('database1.db')
    conn.execute('CREATE TABLE files(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,data TEXT,type TEXT,password TEXT,user INTEGER,created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    conn.close()
    conn = sqlite3.connect('database2.db')
    conn.execute('CREATE TABLE files(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,data TEXT,type TEXT,password TEXT,user INTEGER,created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    conn.close()
    return "Table Created"


if __name__ == '__main__':
   app.run(debug=True)