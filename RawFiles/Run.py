import datetime

try:
    import click
    import itsdangerous
    import jinja2
    import markupsafe
    import werkzeug
    import flask
    import sqlite3
    import os
    import json
    import smtplib
    from email.message import EmailMessage
    import ssl
    import random

    basePath = os.getcwd()
    app = flask.Flask(__name__, template_folder=os.path.join(basePath, 'templates'),
                      static_folder=os.path.join(basePath, 'static'))
    configurationsInfoTXT = json.load(open("config.txt"))

    cok = None
    tempcod = None


    def loadCok(email, passw, nome, cpf, tel=None, end=None, access=0):
        global cok

        cok = [email, passw, nome, cpf, tel, end, access]
        for i, k in enumerate(cok):
            if k == None:
                cok[i] = "Não Definido"


    def unloadCok():
        global cok
        cok = None


    # No url redirect
    @app.route('/')
    def empt():
        return flask.redirect('index')


    @app.route('/index')
    def index():
        return flask.render_template("index.html", u=cok)


    @app.route('/login')
    def login():
        return flask.render_template("login.html")


    @app.route('/sign')
    def sign():
        return flask.render_template("sign.html")


    @app.route('/profile')
    def profileH():
        if cok is None:
            return flask.redirect('/login')
        else:
            return flask.render_template('profile.html', u=cok)


    @app.route('/profile/logout')
    def logout():
        unloadCok()
        return flask.redirect("/login")


    @app.route('/redefinePass')
    def rediPass():
        return flask.render_template("redefinir.html")


    @app.route('/erro')
    def erro():
        return flask.render_template("erro.html")


    @app.route('/doacao')
    def doacao():
        return flask.render_template("doacao.html")


    @app.route('/contact')
    def contact():
        return flask.render_template("contact.html")


    @app.route('/code')
    def redefinecodeV():
        return flask.render_template("redefinircod.html", u=tempcod)


    @app.route('/voluntariof')
    def formularioV():
        return flask.render_template("formularioV.html")


    @app.route('/formSendGeneric')
    def formSendGeneric():
        return flask.render_template("formSendGeneric.html")


    @app.route('/voluntarios')
    def voluntariosLista():
        if cok is None:
            return flask.redirect("/login")
        else:
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM user WHERE access=? AND email=?', (3, cok[0],))
                acc = c.fetchone()

                if acc is not None:
                    with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                        c = conn.cursor()
                        c.execute(
                            "SELECT u.nome, u.email, u.user_id, u.access, v.tipo FROM user u JOIN voluntario v ON u.user_id = v.user_id;")
                        data = c.fetchall()

                        return flask.render_template("voluntariosLista.html", data=data)
                else:
                    return flask.redirect("/erro")


    @app.route('/estoque')
    def estoque():
        if cok is None:
            return flask.redirect("/login")

        else:
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()

                c.execute('SELECT * FROM user WHERE access = ? AND email=?', (3, cok[0]))
                acc = c.fetchone()

                if acc is not None:
                    with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                        c = conn.cursor()
                        c.execute("SELECT cesta_id, alimentos, status, COALESCE(user_id, 'Nenhum') FROM cesta")
                        data = c.fetchall()

                        return flask.render_template("estoque.html", data=data)
                else:
                    return flask.redirect("/erro")


    @app.route('/estoqueAdd')
    def estoqueAdd():
        if cok is None:
            return flask.redirect("/login")

        else:
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM user WHERE access = ? AND email=?', (3, cok[0]))
                acc = c.fetchone()

                if acc is not None:
                    return flask.render_template("estoqueAdd.html")
                else:
                    return flask.redirect("/erro")


    @app.route('/formRenda')
    def formRenda():
        return flask.render_template("rendaForm.html")


    # Form send
    @app.route('/profile/dltProf', methods=['POST'])
    def deleteProfile():
        if cok == None:
            return flask.redirect('/login')
        else:
            email = flask.request.form.get('emailD')
            passw = flask.request.form.get('passD')
            name = flask.request.form.get('nameD')

            if email == cok[0] and passw == cok[1] and name == cok[2]:

                with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM user WHERE email = ? AND pass = ? AND nome = ?", (email, passw, name))

                    return flask.redirect('/login')
            else:
                return flask.redirect('/profile?error=2')


    @app.route('/sign/send', methods=['POST'])
    def registerF():
        # Register
        email = flask.request.form['email']
        passw = flask.request.form['password']
        nome = flask.request.form['nome']

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM user WHERE email = ?", (email,))
            r = c.fetchone()

            if r == None:
                c.execute("INSERT INTO user (nome, email, pass, access) VALUES (?,?,?,?)", (nome, email, passw, 0))

                return flask.redirect("/login")
            else:
                return flask.redirect(f"/sign?error=1&n={nome}&p={passw}")


    @app.route('/login/send', methods=['POST'])
    def loginR():
        # Login
        email = flask.request.form.get('email')
        passw = flask.request.form.get('password')

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()

            # Bypass the sql-injection
            c.execute("SELECT * FROM user WHERE email = ? AND pass = ?", (email, passw))
            r = c.fetchone()

            if r == None:
                return flask.redirect("/login?error=1")
            else:
                loadCok(email, passw, r[1], r[4], r[3], r[5], r[7])

                return flask.redirect('/profile')


    @app.route('/profile/send', methods=['POST'])
    def editProfile():
        Oemail = flask.request.form.get('Oemail')
        email = flask.request.form.get('email')
        end = flask.request.form.get('end')
        tel = flask.request.form.get('tel')
        nome = flask.request.form.get('name')
        cpf = flask.request.form.get('cpf')

        if tel == "Não Definido":
            tel = None
        if end == "Não Definido":
            end = None

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()

            loadCok(email, cok[1], nome, cpf, tel, end)

            if Oemail == email:
                c.execute("UPDATE user SET nome = ?, telefone = ?, endereco = ?"
                          "WHERE email = ?", (nome, tel, end, email))

                return flask.redirect("/profile")
            else:
                # Bypass the sql-injection
                c.execute("SELECT * FROM user WHERE email = ?", (email,))
                r = c.fetchone()

                if r == None:
                    c.execute("UPDATE user SET nome = ?, email = ?, telefone = ?, endereco = ?"
                              "WHERE email = ?", (nome, email, tel, end, Oemail))

                    return flask.redirect("/profile")

                else:
                    return flask.redirect(f"/profile?error=1")


    @app.route('/contact/send', methods=['POST'])
    def contatSend():
        eS = 'hortelaurbana@gmail.com'
        eP = 'qyyq cdht mkzv eguy'
        eM = flask.request.form.get('email')
        ass = flask.request.form.get('ass')

        s = f'Ticket de Ajuda: {datetime.date.today()}'
        b = f"""
            🌱🌿  Obrigado por nos contatar! iremos fazer o possivel sobre o assunto 🌻☀

            Menssagem:     

            {ass}
        """

        em = EmailMessage()
        em['From'] = eS
        em['To'] = eM
        em['Subject'] = s
        em.set_content(b)

        c = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=c) as smtp:
            smtp.login(eS, eP)
            smtp.sendmail(eS, eM, em.as_string())
            # To myself / Mods

            b = f"""
                🌱🌿  Hortelã ticket fale conosco 🌻☀
                De: {eM}
                Menssagem:  

                {ass}
            """

            em.set_content(b)
            smtp.sendmail(eS, eS, em.as_string())

        return flask.redirect("/index")


    @app.route('/redefinePass/send', methods=['POST'])
    def perdeuasenha():
        eM = flask.request.form.get('email')

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM user WHERE email = ?", (eM,))
            r = c.fetchone()

            if r == None:
                return flask.redirect("/redefinePass?error=1")
            else:
                global tempcod
                eS = 'hortelaurbana@gmail.com'
                eP = 'qyyq cdht mkzv eguy'
                ass = random.randint(1000, 9998)
                ePa = flask.request.form.get('pass1')
                tempcod = [ass, eM, ePa]

                s = f'Ticket de Ajuda {datetime.date.today()}'
                b = f"""
                            🌱🌿  Codigo de confirmação para redefinir senha 🌻☀
                            Código expira após 5 minutos   

                            {ass}
                        """

                em = EmailMessage()
                em['From'] = eS
                em['To'] = eM
                em['Subject'] = s
                em.set_content(b)

                c = ssl.create_default_context()

                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=c) as smtp:
                    smtp.login(eS, eP)
                    smtp.sendmail(eS, eM, em.as_string())

                return flask.redirect('/code')


    @app.route('/redefinePassC/send', methods=['POST'])
    def mudarsenha():
        global tempcod

        # Register
        eM = tempcod[1]
        ePa = tempcod[2]

        tempcod = None

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()
            c.execute("UPDATE user SET pass = ? WHERE email = ?", (ePa, eM))

            return flask.redirect("/login")


    @app.route('/voluntariof/send', methods=['POST'])
    def formularioVS():
        # Register
        email = flask.request.form['email']
        nome = flask.request.form['nome']

        cpf = flask.request.form['cpf']
        cpf1 = cpf.replace(".", "")
        cpf2 = cpf1.replace("-", "")

        tel = flask.request.form['tel']
        tel1 = tel.replace(" ", "")
        tel2 = tel1.replace("-", "")

        # Recreate connection each time to prevent threading issues
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM user WHERE email = ?", (email,))
            r = c.fetchone()

            if r is not None:
                c.execute("UPDATE user SET cpf = ?, nome = ?, telefone = ? WHERE email = ?", (cpf2, nome, tel2, email,))

                # Fetch the result
                c.execute("SELECT user_id FROM user WHERE email = ?", (email,))
                r = c.fetchone()
                idU = r[0]

                c.execute("INSERT INTO voluntario (dataDisp, tipo, user_id) VALUES (?,?,?)",
                          ("0000-00-00", "avaliando", idU,))

                return flask.redirect("/voluntarioAvl")
            else:
                return flask.redirect(f"/sign")


    @app.route('/voluntarios/send', methods=['POST'])
    def voluntariosListaS():
        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()

            for key, value in flask.request.form.items():
                if key.startswith('status_'):
                    uid = key.split('_')[1]

                    c.execute('UPDATE voluntario SET tipo = ? WHERE user_id = ?', (value, uid))
            return flask.redirect("/voluntarios")


    @app.route('/estoque/delete', methods=['POST'])
    def estoqueDelete():
        idC = flask.request.form['id']

        with sqlite3.connect(configurationsInfoTXT['data']) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM cesta WHERE cesta_id = ?", idC)

        return flask.redirect("/estoque")


    @app.route('/estoqueAdd/send', methods=['POST'])
    def estoqueSend():
        rec = flask.request.form['receptor']
        alim = flask.request.form['alim']
        stat = flask.request.form['status']

        def addStoque(alime, stats, nome=None):
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO cesta (alimentos, status, user_id) VALUES (?,?,?)", (alime, stats, nome))

        if rec == '':
            addStoque(alim, stat)
            return flask.redirect('/estoque')

        else:
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM user WHERE nome = ?", (rec,))
                r = c.fetchone()

                if r is not None:
                    addStoque(alim, stat, r[0])
                    return flask.redirect('/estoque')
                else:
                    return flask.redirect(f'/estoqueAdd?error=1&n={rec}')


    @app.route('/renda/send', methods=['POST'])
    def formRendaSend():
        if cok is not None:
            ren = flask.request.form['renda']
            dep = flask.request.form['dependentes']
            oR = flask.request.form['outra_renda']
            dP = flask.request.form['despesa_principal']
            gA = flask.request.form['gasto_alimentacao']
            aux = flask.request.form['auxilio']

            def email():
                eS = 'hortelaurbana@gmail.com'
                eP = 'qyyq cdht mkzv eguy'
                s = f'Formulario de renda {cok[0]}'
                b = f"""
                            🌱🌿  Copia da resposta do formulario de renda 🌻☀

                            Respostas:     

                            Renda: {ren}
                            Dependentes: {dep}
                            Outras Rendas: {oR}
                            Despesas Principais: {dP}
                            Gastos da alimentação: {gA}
                            Auxilio: {aux}
                        """

                em = EmailMessage()
                em['From'] = eS
                em['To'] = eS
                em['Subject'] = s
                em.set_content(b)

                c = ssl.create_default_context()

                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=c) as smtp:
                    smtp.login(eS, eP)
                    smtp.sendmail(eS, eS, em.as_string())

            # Recreate connection each time to prevent threading issues
            with sqlite3.connect(configurationsInfoTXT['data']) as conn:
                c = conn.cursor()
                c.execute('UPDATE user SET access = ? WHERE email = ?', (1, cok[0]))
                email()

                return flask.redirect('/formSendGeneric')
        else:
            return flask.redirect('/login')


    if __name__ == '__main__':
        ip = configurationsInfoTXT['ip']
        port = configurationsInfoTXT['port']
        app.run(host=ip, port=port, debug=True)
        os.system("pause")

except Exception as e:
    with open("log.txt", 'w') as f:
        f.write(f"[{datetime.datetime.now()}] {e}\n")