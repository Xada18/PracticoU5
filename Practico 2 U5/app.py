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
            if usuario.clave == request.form['clave']:
                session["usuario"] = request.form['correo']
                return render_template('index.html', tipo=request.form['tipo'])
            else:
                return render_template('login.html', error="La contraseña no es válida")
            
@app.route('/seleccionarFuncion', methods=['GET', 'POST'])
def seleccionarFuncion():
    html = request.args.get('html')
    tipo = request.args.get('tipo')
    if tipo == "preceptor":
        preceptor = Preceptor.query.filter_by(correo=session.get('usuario')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template(template_name_or_list=html, cursos=cursos, tipo=tipo)
    elif tipo == "tutor":
        return render_template(template_name_or_list=html, tipo=tipo)

@app.route('/seleccionar_curso1', methods = ['GET', 'POST'])
def seleccionarCurso1():
    if 'curso' not in request.form or not request.form['curso']:
        preceptor = Preceptor.query.filter_by(correo=session.get('usuario')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template('seleccionar_curso1.html', preceptor=preceptor, cursos=cursos, error="Seleccione un curso", tipo="preceptor")
    else:
        idcurso = request.form['curso']
        estudiantes = Estudiante.query.filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()
        return render_template('registrar_asistencia.html', estudiantes=estudiantes, idcurso=idcurso, tipo="preceptor")

@app.route('/seleccionar_curso2', methods = ['GET', 'POST'])
def seleccionarCurso2():
    if 'curso' not in request.form or not request.form['curso']:
        preceptor = Preceptor.query.filter_by(correo=session.get('usuario')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template('seleccionar_curso2.html', preceptor=preceptor, cursos=cursos, error="Seleccione un curso", tipo="preceptor")
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

        return render_template('informe_con_detalles.html', estudiantes=estudiantes, idcurso=idcurso, contadores=contadores, tipo="preceptor")

@app.route('/seleccionar_curso3', methods=['GET', 'POST'])
def seleccionarCurso3():
    if 'curso' not in request.form or not request.form['curso'] or 'fecha' not in request.form or 'clase' not in request.form or not request.form['fecha'] or not request.form['clase']:
        preceptor = Preceptor.query.filter_by(correo=session.get('usuario')).first()
        cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
        return render_template('seleccionar_curso3.html', preceptor=preceptor, cursos=cursos, error="Seleccione un curso", tipo="preceptor")
    else:
        fecha = request.form['fecha']
        valorclase = request.form['clase']
        if valorclase == "1":
            clase="Clase: Normal"
        elif valorclase == "2":
            clase="Clase: Ed. Fisica"
        idcurso = request.form['curso']
        curso = Curso.query.filter_by(id=idcurso).first()
        asistencias = Asistencia.query.filter_by(fecha=fecha, codigoclase=valorclase).join(Estudiante, Asistencia.idestudiante == Estudiante.id).filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()
        if not asistencias:
            preceptor = Preceptor.query.filter_by(correo=session.get('usuario')).first()
            cursos = Curso.query.filter_by(idpreceptor=preceptor.id).all()
            return render_template('seleccionar_curso3.html', preceptor=preceptor, cursos=cursos, error="Este curso no tiene asistencias registradas de esta clase en la fecha ingresada", tipo="preceptor")
        return render_template('listado_de_asistencia.html', asistencias=asistencias, fecha=fecha, clase=clase, curso=curso, tipo="preceptor")
    
@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
    idcurso = request.form['idcurso']
    estudiantes = Estudiante.query.filter_by(idcurso=idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all()
    
    if 'fecha' not in request.form or 'clase' not in request.form or not request.form['fecha'] or not request.form['clase']:
        return render_template('registrar_asistencia.html', estudiantes=estudiantes, idcurso=idcurso, error="Faltan datos", tipo="preceptor")
    
    else:
        asistencia_existente = Asistencia.query.filter_by(fecha=request.form['fecha']).first()
        if asistencia_existente:
            return render_template('registrar_asistencia.html', estudiantes=estudiantes, idcurso=idcurso, error="Ya existe una asistencia registrada para la fecha seleccionada", tipo="preceptor")
        
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
    
@app.route('/verificarDNI', methods=['GET', 'POST'])
def verificar_dni():
    if 'dni' not in request.form or not request.form['dni']:
        return render_template('verificar_dni.html', tipo="tutor", error="Ingrese DNI")
    else:
        hijo = Estudiante.query.filter_by(dni=request.form['dni']).first()

        if not hijo:
            return render_template('verificar_dni.html', tipo="tutor", error="No existe alumno con el DNI ingresado")
        else:
            inasistencias=Asistencia.query.filter_by(idestudiante=hijo.id, asistio="n").order_by(Asistencia.fecha).all()
            faltas = 0
            for inasistencia in inasistencias:
                if inasistencia.codigoclase == 1:
                    faltas += 1
                elif inasistencia.codigoclase == 2:
                    faltas += 0.5
            return render_template('consultar_inasistencias.html', tipo="tutor",inasistencias=inasistencias, faltas=faltas)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)