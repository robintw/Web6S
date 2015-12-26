from flask import Flask, render_template, redirect, url_for, request, session
from StringIO import StringIO
import sys
sys.path.append('/usr/local/lib/python2.6/dist-packages')
import matplotlib
matplotlib.use('Agg')
from Py6S import *
from matplotlib.pyplot import *
import pickle
import os


app = Flask(__name__)
#app.debug = True

app.secret_key = 'gfen3483krjgnporjregiwnw[pr9jr;ef938r\;\;['


@app.route('/')
@app.route('/index')
def index():
    if 'id' not in session:
        import uuid
        session['id'] = uuid.uuid4()
    return render_template('index.html')


@app.route('/py6sparams', methods=["POST", "GET"])
def params():
    aot = float(request.form['aot'])
    return run(aot)


@app.route('/py6s/<aot>')
def run(aot):
    s = SixS()
    s.altitudes.set_target_sea_level()
    s.altitudes.set_sensor_satellite_level()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(GroundReflectance.GreenVegetation)
    s.aot550 = float(aot)
    results = SixSHelpers.Wavelengths.run_vnir(s, spacing=0.1, output_name="apparent_radiance")

    xs = ",".join(map(str, list(results[0])))
    ys = ",".join(map(str, list(results[1])))

    return redirect(url_for('show', x=xs, y=ys, params="none", lab="AOT = %.2f" % s.aot550))


@app.route('/show/<x>/<y>')
@app.route('/show/<x>/<y>/<params>')
@app.route('/show/<x>/<y>/<params>/<lab>')
def show(x, y, params="", lab=""):
    if params == "clear":
        clf()
    xvals = map(float, x.split(','))
    yvals = map(float, y.split(','))

    path = '/tmp/%s.pickle' % session['id']
    if os.path.exists(path):
        fig, axes = pickle.load(file(path))
    else:
        fig, axes = subplots()

    colors = ['blue', 'red', 'green', 'orange', 'black']
    n_lines = len(axes.lines)

    axes.plot(xvals, yvals, color=colors[n_lines], label=lab)
    axes.legend()

    axes.set_xlabel("Wavelength ($\mu m$)")
    axes.set_ylabel("Radiance ($W/m^2/sr$)")

    pickle.dump((fig, axes), file(path, 'w'))

    img = StringIO()
    fig.savefig(img)
    img.seek(0)

    return img.getvalue().encode("base64").strip()


@app.route('/clear')
def clear():
    path = '/tmp/%s.pickle' % session['id']

    os.remove(path)
    del session['id']
    redirect('index')

if __name__ == '__main__':
    app.run(debug=True)
