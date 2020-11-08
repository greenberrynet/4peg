import os
import re
import flask
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from werkzeug.utils import secure_filename
import subprocess
import datetime
from app.forms import LoginForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from passlib.hash import sha256_crypt

ALLOWED_EXTENSIONS = set(['csv','j2','txt'])

app = Flask(__name__)
CSV_FOLDER = os.path.join(app.root_path, 'csv')
TEMPLATE_FOLDER = os.path.join(app.root_path, 'jinja2')
CONFIG_FOLDER = os.path.join(app.root_path, 'configs')
LOG_FOLDER = os.path.join(app.root_path, 'logs')
DHCP_FOLDER = '/var/lib/dhcp/'
PROVISION_SCRIPT = os.path.join(app.root_path, 'provision.py')
APPLY_CONFIG_SCRIPT = '/var/lib/dhcp/scrape_dhcpd_leases.py'
app.config['SECRET_KEY'] = '0klandf2p3nava311nasnfoaewi2030asd'
app.config['CSV_FOLDER'] = CSV_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER
app.config['CONFIG_FOLDER'] = CONFIG_FOLDER
app.config['LOG_FOLDER'] = LOG_FOLDER
app.config['DHCP_FOLDER'] = DHCP_FOLDER
# Set the max upload size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')

#app.secret_key = '0klandf2p3nava311nasnfoaewi2030asd'
login_manager = LoginManager(app)

users = {'nimda':{'password':'$5$rounds=535000$uKOkF9roKAA2xCxV$86KJgA7lr3t5NwqHp/5CwYqnlmcE54nGJB.XgRtNoC9'}}

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    form_password = request.form['password']
    if sha256_crypt.verify(form_password, users[username]['password'] ):
        user.authenticated = True

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('This is a restricted area. Please sign in.')
    return redirect(url_for('login'))



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def app_main():
    return render_template('main.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #flash('Login requested for user {}, remember_me={}'.format(form.username.data,form.remember_me.data))
        username = request.form['username']
        form_password = request.form['password']
        crypt_password = sha256_crypt.encrypt('form_password')
        if sha256_crypt.verify(form_password, users[username]['password'] ):
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('csv'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    if logout_user():
        flash("Logged out..")
    return redirect(url_for('login'))

@app.route('/csv/')
#@login_required
def csv():
    # Show directory contenots
    files = os.listdir(CSV_FOLDER)
    return render_template('files.html', files=files, file_type='csv')

@app.route('/upload', methods=['GET', 'POST'])
#@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        file_type = request.form['file_type']
        if 'file' not in request.files:
            #flash('No file part')
            #return redirect(request.url)
            return 'No File'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if file_type == 'csv': 
                file.save(os.path.join(app.config['CSV_FOLDER'], filename))
                return redirect(url_for('csv'))
            if file_type == 'template': 
                file.save(os.path.join(app.config['TEMPLATE_FOLDER'], filename))
                return redirect(url_for('template'))
            if file_type == 'config': 
                file.save(os.path.join(app.config['CONFIG_FOLDER'], filename))
                return redirect(url_for('config'))
            #return redirect(url_for('uploaded_file', filename=filename))
            #return redirect(url_for('csv'))
            return redirect(url_for(request.referrer))
		
    return render_template('upload.html')

@app.route('/delete_file/<file_type>/<filename>')
#@login_required
def delete_file(file_type,filename):
    if file_type == 'csv':
        FOLDER = app.config['CSV_FOLDER']
    if file_type == 'template':
        FOLDER = app.config['TEMPLATE_FOLDER']
    if file_type == 'config':
        FOLDER = app.config['CONFIG_FOLDER']
    if file_type == 'dhcp':
        FOLDER = app.config['DHCP_FOLDER']
    if file_type == 'logs':
        FOLDER = app.config['LOG_FOLDER']
    filename = os.path.join(FOLDER,filename)
    os.remove(filename)
    return redirect(url_for(file_type))
 

@app.route('/open_file/<file_type>/<filename>')
#@login_required
def open_file(file_type,filename):
    if file_type == 'csv':
        FOLDER = app.config['CSV_FOLDER']
    if file_type == 'template':
        FOLDER = app.config['TEMPLATE_FOLDER']
    if file_type == 'config':
        FOLDER = app.config['CONFIG_FOLDER']
    if file_type == 'dhcp':
        FOLDER = app.config['DHCP_FOLDER']
    if file_type == 'logs':
        FOLDER = app.config['LOG_FOLDER']
    filename =  os.path.join(FOLDER,filename)
    with open(filename, "r") as f:
        content = f.read()
    return render_template('open_file.html', content=content)
 

@app.route('/archive_file/<file_type>/<filename>')
#@login_required
def archive_file(file_type,filename):
    if file_type == 'csv':
        FOLDER = app.config['CSV_FOLDER']
    if file_type == 'template':
        FOLDER = app.config['TEMPLATE_FOLDER']
    if file_type == 'config':
        FOLDER = app.config['CONFIG_FOLDER']
    if file_type == 'dhcp':
        FOLDER = app.config['DHCP_FOLDER']
    if file_type == 'logs':
        FOLDER = app.config['LOG_FOLDER']
    filename = os.path.join(FOLDER,filename)
    archive_filename = ('%s-%s.%s', (filename.split('.')[0],timestamp,filename.split('.')[1])) 
    archive_folder = os.path.join(FOLDER,'archive/')
    subprocess.Popen(["mv %s %s%s" % (filename,archive_folder,archive_filename)], shell=True)

    os.remove(filename)
    return redirect(url_for(file_type))

@app.route('/download/<file_type>/<filename>')
#@login_required
def download(file_type,filename):
    if file_type == 'csv':
        FOLDER = app.config['CSV_FOLDER']
    if file_type == 'template':
        FOLDER = app.config['TEMPLATE_FOLDER']
    if file_type == 'config':
        FOLDER = app.config['CONFIG_FOLDER']
    if file_type == 'logs':
        FOLDER = app.config['LOG_FOLDER']
    return send_from_directory(FOLDER, filename)



@app.route('/config/')
#@login_required
def config():
    # Show directory contents
    files = os.listdir(CONFIG_FOLDER)
    return render_template('files.html', files=files, file_type='config')


@app.route('/template/')
#@login_required
def template():
    # Show directory contents
    files = os.listdir(TEMPLATE_FOLDER)
    return render_template('files.html', files=files, file_type='template')

@app.route('/logs/')
#@login_required
def logs():
    # Show directory contents
    files = os.listdir(LOG_FOLDER)
    return render_template('files.html', files=files, file_type='logs')

@app.route('/build/')
#@login_required
def build():
    csv_files = os.listdir(CSV_FOLDER)
    template_files = os.listdir(TEMPLATE_FOLDER)
    return render_template('build.html', csv_files=csv_files, template_files=template_files)


@app.route('/build_run/',  methods=['GET', 'POST'])
#@login_required
def build_run():
    # Show directory contentso
    if request.method == 'POST':
        csv_file = "./csv/" + request.form['csv_file']
        template_file = "./jinja2/" + request.form['template_file']
        provisioning_script = PROVISION_SCRIPT + " -c " + csv_file + " -t " + template_file + " -d ./configs/"
        script_output = subprocess.getoutput(provisioning_script)
        return render_template('build_run.html', output=script_output)
    return redirect(url_for(build))


@app.route('/apply_config/',  methods=['GET', 'POST'])
#@login_required
def apply_config():
    # Show directory contentso
    provisioning_script = APPLY_CONFIG_SCRIPT
    script_output = subprocess.getoutput(provisioning_script)
    script_output_html = re.sub('\n','<br>',script_output)
    return render_template('apply_config.html', output=script_output_html)



if __name__ == '__main__':
# Dev
#   app.run(host='0.0.0.0', port=8001, ssl_context='adhoc', debug = True)
# Prod
   app.run(host='0.0.0.0', port=8000, ssl_context='adhoc', debug = False)
