from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
)
import sendgrid
from sendgrid.helpers.mail import *

from app.database import get_db

# crear blueprint
bp = Blueprint("mail", __name__,url_prefix="/")

#ruta raiz (listado de correos enviados)
@bp.route("/", methods=["GET"])
def index():
    search = request.args.get('search') # request.args busca los parametros ingresados en la url
    db, c = get_db()
    if  search is None:
        c.execute("SELECT * FROM email;")
    else:
        c.execute("SELECT * FROM email WHERE content like %s", ('%' + search + '%', ))
        
    mails = c.fetchall()

    return render_template("mails/index.html", mails=mails)

#ruta para crear y enviar correos
@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []

        if not email:
            errors.append("Ingrese un Email")
        if not subject:
            errors.append("Ingrese un Asunto")
        if not content:
            errors.append("Ingrese un Contenido")

        if len(errors) == 0:
            send(email, subject, content)
            db, c = get_db()
            c.execute("INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)", (email, subject, content))
            db.commit()

            return redirect(url_for("mail.index"))
        else:
            for error in errors:
                flash(error)

    return render_template("mails/create.html")

def send(to, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_KEY"])
    from_email = Email(current_app.config["FROM_EMAIL"])
    to_email= To(to)
    content = Content("text/plain", content)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response)




