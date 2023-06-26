from flask import Flask, render_template, request, session

#from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db 
from models import Preceptor, Padre, Estudiante, Asistencia, Curso


@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():

    if not request.form['correo'] or not request.form['clave'] or not request.form['tipo']:
        return render_template('login.html', error="Los datos ingresados no son correctos")
    else:
        usuario=None

        if request.form['tipo'] == "preceptor":
            usuario = Preceptor.query.filter_by(correo=request.form['correo']).first()
            
        elif request.form['tipo'] == "tutor":
            usuario = Padre.query.filter_by(correo=request.form['correo']).first()
        
        if usuario is None:
            return render_template('login.html', error="El correo no esta registrado")
        else:
            session["preceptor"] = request.form['correo']
            if usuario.clave == request.form['clave']:
                return render_template('index.html', tipo=request.form['tipo'])
            else:
                return render_template('login.html', error="La contraseña no es válida")
            




@app.route('/func1', methods = ['GET', 'POST'])
def funcion1():
    preceptor = Preceptor.query.filter_by(correo=session.get('preceptor')).first()
    cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
    return render_template('seleccionar_curso1.html', preceptor=preceptor, cursos=cursos)

@app.route('/seleccionar_curso1', methods = ['GET', 'POST'])
def seleccionarCurso1():
    if 'curso' not in request.form or not request.form['curso']:
        preceptor = Preceptor.query.filter_by(correo=session.get('preceptor')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template('seleccionar_curso1.html', preceptor=preceptor, cursos=cursos, error="Seleccione un curso")
    else:
        idcurso = request.form['curso']
        estudiantes = Estudiante.query.filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()
        return render_template('registrar_asistencia.html', estudiantes=estudiantes, idcurso=idcurso)

@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
    idcurso = request.form['idcurso']
    estudiantes = Estudiante.query.filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()
    
    if 'fecha' not in request.form or 'clase' not in request.form or not request.form['fecha'] or not request.form['clase']:
        return render_template('registrar_asistencia.html', estudiantes=estudiantes, idcurso=idcurso, error="Faltan datos")
    
    else:
        for estudiante in estudiantes:

            asist = str(estudiante.id) + "/asistio"

            if asist in request.form:
                asistio="s"
                justificacion=""

            else:
                asistio="n"

                just = str(estudiante.id) + "/justificacion"

                if just in request.form and request.form[just]:
                    justificacion=request.form[just]
                else:
                    justificacion=""

            asistencia = Asistencia(fecha=request.form['fecha'], codigoclase=request.form['clase'], asistio=asistio, justificacion=justificacion, idestudiante = estudiante.id)

            db.session.add(asistencia)
            db.session.commit()

        return render_template("index.html", tipo="preceptor")





@app.route('/func2')
def funcion2():
    preceptor = Preceptor.query.filter_by(correo=session.get('preceptor')).first()
    cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
    return render_template('seleccionar_curso2.html', preceptor=preceptor, cursos=cursos)

@app.route('/seleccionar_curso2', methods = ['GET', 'POST'])
def seleccionarCurso2():
    if 'curso' not in request.form or not request.form['curso']:
        preceptor = Preceptor.query.filter_by(correo=session.get('preceptor')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template('seleccionar_curso2.html', preceptor=preceptor, cursos=cursos, error="Seleccione un curso")
    else:
        idcurso = request.form['curso']
        estudiantes = Estudiante.query.filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()

        
        contadores=[]

        for estudiante in estudiantes:
            asistencias = Asistencia.query.filter_by(idestudiante=estudiante.id).all()

            asists1 = 0
            asists2 = 0
            faltas1 = 0
            faltas2 = 0
            justificadas1 = 0
            justificadas2 = 0
            

            for asistencia in asistencias:
                if asistencia.asistio == "s":
                    if asistencia.codigoclase == 1:
                        asists1 +=1
                    elif asistencia.codigoclase == 2:
                        asists2 +=1
                elif asistencia.asistio == "n":
                    if asistencia.codigoclase == 1:
                        faltas1 +=1
                        if asistencia.justificacion:
                            justificadas1+=1
                    elif asistencia.codigoclase == 2:
                        faltas2 +=1
                        if asistencia.justificacion:
                            justificadas2+=1
            
            conts=[asists1, asists2, faltas1, faltas2, justificadas1, justificadas2]

            contadores.append(conts)

        return render_template('informe_con_detalles.html', estudiantes=estudiantes, idcurso=idcurso, contadores=contadores)

@app.route('/informe_con_detalles')
def informeConDetalles():
    pass





@app.route('/func3')
def funcion3():
    return render_template('listado_de_asistencia.html')








if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)