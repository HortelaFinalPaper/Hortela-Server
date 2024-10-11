import datetime
try:
    import click
    import itsdangerous
    import jinja2
    import markupsafe
    import werkzeug
    import flask
    import os
    import json
    import smtplib
    from email.message import EmailMessage
    import ssl
    import random
    import pyodbc

    basePath = os.getcwd()
    app = flask.Flask(__name__, template_folder=os.path.join(basePath, 'templates'), static_folder=os.path.join(basePath, 'static'))
    configurationsInfoTXT = json.load(open("config.txt"))
    # database get
    def get_db_connection():
        conn_str = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={configurationsInfoTXT["host"]},{configurationsInfoTXT["portdb"]};'
            f'DATABASE={configurationsInfoTXT["database"]};'
            f'UID={configurationsInfoTXT["user"]};'
            f'PWD={configurationsInfoTXT["password"]};'
            'Encrypt=no;'
        )
        conn = pyodbc.connect(conn_str)
        return conn

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

    @app.route('/termos.pdf')
    def termos():
        return flask.send_from_directory('static', 'termos.pdf')
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
    def voluntariosLista():
        if cok is None:
            return flask.redirect("/login")
        else:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE access=? AND email=?', (3, cok[0],))
                acc = c.fetchone()

                if acc is not None:
                    c.execute(
                        "SELECT u.nome, u.email, u.user_id, u.access, v.tipo FROM users u JOIN voluntario v ON u.user_id = v.user_id;")
                    data = c.fetchall()

                    return flask.render_template("voluntariosLista.html", data=data)
                else:
                    return flask.redirect("/erro")
    @app.route('/estoque')
    def estoque():
        if cok is None:
            return flask.redirect("/login")
        else:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM s WHERE access = ? AND email=?', (3, cok[0]))
                acc = c.fetchone()

                if acc is not None:
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
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE access = ? AND email=?', (3, cok[0]))
                acc = c.fetchone()

                if acc is not None:
                    return flask.render_template("estoqueAdd.html")
                else:
                    return flask.redirect("/erro")
    @app.route('/formRenda')
    def formRenda():
        return flask.render_template("rendaForm.html")
    @app.route('/voluntarioCalendario')
    def calendario():
        pass

    @app.route('/profile/dltProf', methods=['POST'])
    def deleteProfile():
        if cok == None:
            return flask.redirect('/login')
        else:
            email = flask.request.form.get('emailD')
            passw = flask.request.form.get('passD')
            name = flask.request.form.get('nameD')

            if email == cok[0] and passw == cok[1] and name == cok[2]:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE email = ? AND pass = ? AND nome = ? ",(email, passw, name))
                    conn.commit()
                return flask.redirect('/login')
            else:
                return flask.redirect('/profile?error=2')
    @app.route('/sign/send', methods=['POST'])
    def registerF():
        email = flask.request.form['email']
        passw = flask.request.form['password']
        nome = flask.request.form['nome']

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? ", (email,))
            r = cursor.fetchone()

            if r is None:
                cursor.execute("INSERT INTO users (nome, email, pass, access) VALUES (?,?,?,?)",
                               (nome, email, passw, 0))
                conn.commit()
                return flask.redirect("/login")
            else:
                return flask.redirect(f"/sign?error=1&n={nome}&p={passw}")
    @app.route('/login/send', methods=['POST'])
    def loginR():
        email = flask.request.form.get('email')
        passw = flask.request.form.get('password')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND pass = ?", (email, passw))
            r = cursor.fetchone()

            if r is None:
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

        with get_db_connection() as conn:
            cursor = conn.cursor()

            loadCok(email, cok[1], nome, cpf, tel, end)

            if Oemail == email:
                cursor.execute("UPDATE users SET nome = ?, telefone = ?, endereco = ? WHERE email = ?",
                               (nome, tel, end, email))
                conn.commit()
                return flask.redirect("/profile")
            else:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                r = cursor.fetchone()

                if r is None:
                    cursor.execute(
                        "UPDATE users SET nome = ?, email = ?, telefone = ?, endereco = ? WHERE email = ?",
                        (nome, email, tel, end, Oemail))
                    conn.commit()
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
            🌱🌿  Obrigado por nos contatar! Iremos fazer o possível sobre o assunto 🌻☀

            Mensagem:     

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

            # Enviar cópia para si mesmo
            b = f"""
                🌱🌿  Hortelã ticket fale conosco 🌻☀
                De: {eM}
                Mensagem:  

                {ass}
            """
            em.set_content(b)
            smtp.sendmail(eS, eS, em.as_string())

        return flask.redirect("/index")
    @app.route('/redefinePass/send', methods=['POST'])
    def perdeuasenha():
        eM = flask.request.form.get('email')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (eM,))
            r = cursor.fetchone()

            if r is None:
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
                    🌱🌿  Código de confirmação para redefinir senha 🌻☀
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

        eM = tempcod[1]
        ePa = tempcod[2]
        tempcod = None

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET pass = ? WHERE email = ?", (ePa, eM))
            conn.commit()

        return flask.redirect("/login")
    @app.route('/voluntariof/send', methods=['POST'])
    def formularioVS():
        email = flask.request.form['email']
        nome = flask.request.form['nome']

        cpf = flask.request.form['cpf'].replace(".", "").replace("-", "")
        tel = flask.request.form['tel'].replace(" ", "").replace("-", "")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            r = cursor.fetchone()

            if r is not None:
                cursor.execute("UPDATE users SET cpf = ?, nome = ?, telefone = ? WHERE email = ?",
                               (cpf, nome, tel, email))
                conn.commit()

                cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
                r = cursor.fetchone()
                idU = r[0]

                cursor.execute("INSERT INTO voluntario (dataDisp, tipo, user_id) VALUES (?,?,?,?)",
                               ("0000-00-00", "avaliando", idU))
                conn.commit()

                return flask.redirect("/voluntarioAvl")
            else:
                return flask.redirect(f"/sign")
    @app.route('/voluntarios/send', methods=['POST'])
    def voluntariosListaS():
        with get_db_connection() as conn:
            cursor = conn.cursor()

            for key, value in flask.request.form.items():
                if key.startswith('status_'):
                    uid = key.split('_')[1]
                    cursor.execute('UPDATE voluntario SET tipo = ? WHERE user_id = ?', (value, uid))
                    conn.commit()

        return flask.redirect("/voluntarios")
    @app.route('/estoque/delete', methods=['POST'])
    def estoqueDelete():
        idC = flask.request.form['id']

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cesta WHERE cesta_id = ?", (idC,))
            conn.commit()

        return flask.redirect("/estoque")
    @app.route('/estoqueAdd/send', methods=['POST'])
    def estoqueSend():
        rec = flask.request.form['receptor']
        alim = flask.request.form['alim']
        stat = flask.request.form['status']

        def addStoque(alime, stats, nome=None):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO cesta (alimentos, status, user_id) VALUES (?,?,?)",
                               (alime, stats, nome))
                conn.commit()

        if rec == '':
            addStoque(alim, stat)
            return flask.redirect('/estoque')
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE nome = ?", (rec,))
                r = cursor.fetchone()

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

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET access = ? WHERE email = ?', (1, cok[0]))
                conn.commit()
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