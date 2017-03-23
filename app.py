from subprocess import call
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import script as s
import time

UPLOAD_FOLDER = 'local/inputs'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #  return redirect(url_for('uploaded_file',
            #                          filename=filename))
            result = s.run_script(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if result != False:
                #  return redirect("http://http://138.197.5.177/" +result , code=302)
                #  src1 = "http://138.197.5.177/" +result + "/output1.jpg"
                #  src2 = "http://138.197.5.177/" +result + "/output2.jpg"
                #  src3 = "http://138.197.5.177/" +result + "/output3.jpg"
                call(['ffmpeg', '-framerate', '1', '-i', result + "/output%01d.jpg", result + "/output.mp4"])
                time.sleep(2)
                call(['ffmpeg', '-i', result + "/output.mp4", result+"/output.gif"])
                src = "http://138.197.5.177/" +result + "/output.gif"
                return render_template('results.html', src1=src)
            return '''
                <!doctype html>
                <title>Upload new File</title>
                <h1>Upload new File</h1>
                <form method=post enctype=multipart/form-data>
                  <p><input type=file name=file>
                     <input type=submit value=Upload>
                </form>
            '''
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
    })

if __name__ == "__main__":
    app.run()

