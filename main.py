#import servidor as s
from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
import sys

# class NombrarMesa(QDialog):
#     def __init__(self, msj):
#         super().__init__()
#         loadUi("dialog.ui", self)
#         self.setWindowFlags(Qt.WindowStaysOnTopHint)
#         if msj == 1:
#             self.msjBienvenida.setMaximumHeight(0)

#         self.btnGuardar.clicked.connect(self.GuardarNombres)
#         self.Nombres()

#     def Nombres(self):
#         self.cursor.execute("SELECT * FROM tabMesa")
#         mesa = self.cursor.fetchone()

#         self.nomPresidente.setText(mesa["Presidente"] or "")
#         self.nomModerador.setText(mesa["Moderador"] or "")
#         self.nomSecretario.setText(mesa["Secretario"] or "")
#         self.nomEvaluador.setText(mesa["Evaluador"] or "")
#         self.nomForo.setText(mesa["Foro"] or "")
#         self.ano.setText(str(mesa["Año"]) or "")

#     def GuardarNombres(self):
#         presidente = self.nomPresidente.text() or None
#         moderador = self.nomModerador.text() or None
#         secretario = self.nomSecretario.text() or None
#         evaluador = self.nomEvaluador.text() or None
#         foro = self.nomForo.text().upper() or None
#         ano = self.ano.text() or None
#         self.cursor.execute(f"UPDATE tabMesa SET Presidente= ?, Moderador= ?, Secretario= ?, Evaluador= ?, Foro = ?, Año = ?;", (presidente, moderador, secretario, evaluador, foro, ano))
#         self.conn.commit()
#         self.close()

#     def closeEvent(self, a0):
#         if self.nomForo.text():
#             super().closeEvent(a0)
#         else:
#             a0.ignore()

class HistorialObservaciones(QMainWindow):
    def __init__(self):
        super().__init__()
        self.SERVIDOR = "http://127.0.0.1:5000"  #Va a ser el link a render!!
        loadUi("historialObs.ui", self)

        self.tabHistorial.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabHistorial.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabHistorial.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        observaciones = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo":"""SELECT tabDelegaciones.nomDelegacion, tabDelegados.nomDelegado, tabPuntaje.descObs, tabPuntaje.puntaje FROM tabPuntaje
                                                                                            INNER JOIN tabDelegados ON tabDelegados.idDelegado = tabPuntaje.idDelegado
                                                                                            INNER JOIN tabDelegaciones ON tabDelegaciones.idDelegacion = tabDelegados.idDelegacion 
                                                                                            ORDER BY nomDelegacion DESC"""}).json()
        for observacion in observaciones:
            self.tabHistorial.insertRow(0)
            self.tabHistorial.setItem(0, 0, QTableWidgetItem(observacion["nomDelegacion"]))
            self.tabHistorial.setItem(0, 1, QTableWidgetItem(observacion["nomDelegado"]))
            self.tabHistorial.setItem(0, 2, QTableWidgetItem(observacion["descObs"]))
            self.tabHistorial.setItem(0, 3, QTableWidgetItem(str(observacion["puntaje"])))

##cada sesion tiene que tener también una fila en tabCambios !

class CEPBMOON(QMainWindow):
    def __init__(self):
        self.SERVIDOR = "http://127.0.0.1:5000"  #Va a ser el link a render!!
        super().__init__()
        loadUi("main.ui", self)
        self.ConectarFunciones()                        # Se llaman todas la funciones
        self.Buscador()                                 

        self.CrearFila()
        self.CrearHistorial()

        # self.NombrarMesaAlAbrir()                       
        # self.PaisesEnForo()                             
        # self.DelegacionesEnForo(self.Delegados)
        # self.Configuraciones()
        # self.Cronometro()
        self.Observaciones()

    def ConectarFunciones(self):    # Conecta los botones principales con sus funciones
        self.btn1.clicked.connect(lambda _, c=self.Configuraciones_2: self.Expandir(c))
        self.btn2.clicked.connect(lambda _, c=self.Anotaciones_2: self.Expandir(c))
        self.btn3.clicked.connect(lambda _, c=self.Cronometro_2: self.Expandir(c))
        self.btn4.clicked.connect(lambda _, c=self.Historial: self.Expandir(c))

        #Ajusta el layout de la fila de delegaciones
        self.scrollLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)
  
        self.cerrarSideBar.clicked.connect(lambda: self.sideBar.setMaximumWidth(0))
        self.btnLimpiar.clicked.connect(self.LimpiarFila)
        self.listaForo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.listaHistorial.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   

        self.correrGETs = QTimer(self)
        self.correrGETs.timeout.connect(self.Gets)
        self.correrGETs.start(1000)

    def LimpiarFila(self):
        self.LimpiarLayout(self.scrollLayout)
        requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "delete from tabFila"})
        requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "UPDATE tabCambios SET hayCambios = 1, fila = 1;"})
    
    def Gets(self):
        cambios = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": "SELECT * FROM tabCambios"}).json()
        if cambios[0]["hayCambios"]:
            if cambios[0]["fila"]:
                self.CrearFila()
            if cambios[0]["historial"]:
                self.CrearHistorial()
            requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "UPDATE tabCambios SET hayCambios = 0, fila = 0, historial = 0;"})
        self.correrGETs.start(1000)

    def Buscador(self):              # Actualizar el buscador cuando se cambia los paises en un foro
        delegaciones = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": "SELECT nomDelegacion FROM tabDelegaciones"}).json()
        self.delegaciones = [fila["nomDelegacion"] for fila in delegaciones]
        self.completer = QCompleter(self.delegaciones)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.txtDelegacion.setCompleter(self.completer)
 
        self.txtBuscador.returnPressed.connect(self.Buscar)
        self.btnBuscar.clicked.connect(self.Buscar)

    def NombrarMesaAlAbrir(self):    # Abre el menú para nombrar a los miembros de la mesa, primero comprueba que esté completa paa abrirlo
        self.cursor.execute("SELECT Presidente, Moderador, Secretario, Evaluador, Foro, Año FROM tabMesa")
        mesa = self.cursor.fetchone()
        if None in mesa:
            self.nombrarMesa = NombrarMesa(0)
            self.nombrarMesa.setModal(True) 
            self.nombrarMesa.show()

    def Buscar(self):                # Para buscar un pais y que se añada a la lista de oradores
        delegacion = self.txtBuscador.text().strip()
        if not delegacion or delegacion not in self.delegaciones:       # Termina la función si no hay una delegacion en el buscador
            return 
        for i in range(self.scrollLayout.count()):                      # Termina la función si la delegación ya está en la fila
            item = self.scrollLayout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QPushButton) and widget.text() == delegacion:
                self.txtBuscador.clear()
                return
        requests.post(self.SERVIDOR + "/POSTfila_delegaciones", json={"delegacion": delegacion})
        requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "UPDATE tabCambios SET hayCambios = 1, fila = 1;"})
        self.txtBuscador.clear()

    def CrearFila(self):             # Actualiza la fila de delegaciones en cola
        codigo = "SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion ORDER BY tabFila.idFila"
        fila = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": codigo}).json()
        self.LimpiarLayout(self.scrollLayout)
        for delegacion in fila:
            btn = QPushButton(delegacion["nomDelegacion"])
            btn.setMinimumSize(100, 100)
            btn.setMaximumSize(100, 100)
            btn.setStyleSheet('font: 10pt "Bahnschrift SemiBold"; text-align: left; background-color: rgb(255, 255, 255); border-radius: 20px; padding-left: 20px; margin-bottom: 3px;')
            btn.clicked.connect(lambda _, b=btn: self.QuitarPais(b))
            self.scrollLayout.addWidget(btn, alignment=Qt.AlignTop)
        self.scrollLayout.addStretch()
                
    def QuitarPais(self, delegacion):      # Afecta el *Historial*. Quitar un pais de la lista de oradores, registrar y cronometrarlo 
        def Registrar(nomDelegacion):      # Añade el pais al historial
                turnos = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": f"""SELECT tabHistorial.turnos FROM tabHistorial 
                                                                                              INNER JOIN tabDelegaciones ON tabHistorial.idDelegacion = tabDelegaciones.idDelegacion 
                                                                                              WHERE tabDelegaciones.nomDelegacion = '{nomDelegacion}';"""}).json()
                try:
                    turnos = turnos[0]["turnos"]
                except:
                    turnos = 0
                requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": """INSERT INTO tabHistorial (idDelegacion, turnos)
                                                                                      SELECT idDelegacion, %s FROM tabDelegaciones 
                                                                                      WHERE tabDelegaciones.nomDelegacion = %s""", "params":(turnos+1, nomDelegacion,)})
                requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "UPDATE tabCambios SET hayCambios = 1, historial = 1;"})
        def Cronometrar(tiempo):     # Inicia el cronómetro para las delegaciones
            def Cronometro(pais):
                if self.time == QTime(0, 0, 0):
                    self.timer.stop()

                    if tiempo == "pensar":
                        Cronometrar("contestar")
                    else:
                        self.txtCronometro.setText(f"00:00")
                    return
                
                self.time = self.time.addSecs(-1)
                timeDisplay = self.time.toString("mm:ss")
                self.txtCronometro.setText(f"{timeDisplay} - {pais}")
            
            self.Lectura.setEnabled(False)
            self.Cuestionar.setEnabled(False)
            self.Contestar.setEnabled(False)

            self.cursor.execute(f"SELECT {tiempo} FROM tabTiempos")
            t = self.cursor.fetchone()
            self.time = QTime(0, 0, 0)
            self.time = self.time.addSecs(int(t[f"{tiempo}"]))
            self.txtCronometro.setText(f"{self.time.toString("mm:ss")} - {str(pais.text())}")
            try:
                self.timer.timeout.disconnect()
            except:
                pass
            self.timer.timeout.connect(lambda: Cronometro(str(pais.text())))
            self.timer.start(1000)

        nomDelegacion = delegacion.text()
        delegacion.deleteLater()

        id = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": f"SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion = '{nomDelegacion}';"}).json()
        requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "delete from tabFila where idDelegacion=%s;", "params":(id[0]['idDelegacion'],)})
        requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": "UPDATE tabCambios SET hayCambios = 1, fila = 1;"})

        self.timer = QTimer()

        self.txtCronometro.setText(str(nomDelegacion))
        self.Lectura = QShortcut(QKeySequence("l"), self)
        self.Cuestionar = QShortcut(QKeySequence("c"), self)
        self.Contestar = QShortcut(QKeySequence("r"), self)
        self.Lectura.activated.connect(lambda: Cronometrar("leer"))
        self.Cuestionar.activated.connect(lambda: Cronometrar("cuestionar"))
        self.Contestar.activated.connect(lambda: Cronometrar("pensar"))
        Registrar(nomDelegacion)

    def CrearHistorial(self):
        codigo = """SELECT tabDelegaciones.nomDelegacion, tabHistorial.turnos FROM tabDelegaciones
                    INNER JOIN tabHistorial ON tabDelegaciones.idDelegacion = tabHistorial.idDelegacion 
                    ORDER BY tabHistorial.idHistorial"""
        fila = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": codigo}).json()
        self.listaHistorial.clearContents()
        for delegacion in fila:
            self.listaHistorial.insertRow(0)
            self.listaHistorial.setItem(0, 0, QTableWidgetItem(delegacion["nomDelegacion"]))
            self.listaHistorial.setItem(0, 1, QTableWidgetItem(str(delegacion["turnos"])))

    def Observaciones(self):         # Agenda las observaciones
        def AbrirHistorial():                   # Abre el historial de observaciones
            self.verObservaciones = HistorialObservaciones()
            self.verObservaciones.show()

        def AnotarObservacion(idObs):     # Añade la observación a la base de datos, reinicia el menú
            if self.delegado:
                params = [idObs, self.txtObservacion.toPlainText(), self.numPuntaje.text(), self.delegado]
                requests.post(self.SERVIDOR + "/POSTpasar_codigo", json={"codigo": """INSERT INTO tabPuntaje (idDelegado, idObs, descObs, puntaje)
                                                                                      SELECT idDelegado, %s, %s, %s
                                                                                      FROM tabDelegados
                                                                                      WHERE tabDelegados.nomDelegado = %s""",
                                                                                      "params": params})
                self.delegado=""
                self.txtDelegacion.setText(self.txtObservacion.setText(""))
                self.numPuntaje.setValue(0)
        def ElegirDelegado(pais):               # Selecciona bajo que delegado se guardará la observación
            colores = ["font: 11pt 'Bahnschrift SemiLight'; background-color: #bbb; border-radius: 15px; margin-left: 5px; padding-left:5px;", "font: 11pt 'Bahnschrift SemiLight'; background-color: #ddd; border-radius: 15px; margin-left: 5px; padding-left:5px;"]
            try:
                delegados = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": """SELECT nomDelegado FROM tabDelegados 
                                                                                                INNER JOIN tabDelegaciones 
                                                                                                ON tabDelegados.idDelegacion = tabDelegaciones.idDelegacion 
                                                                                                WHERE tabDelegaciones.nomDelegacion = %s;""", 
                                                                                                "params": [pais]}).json()
                self.btnD1.setText((str(delegados[0]["nomDelegado"])) if delegados[0]["nomDelegado"] != None else "")
                self.btnD2.setText((str(delegados[1]["nomDelegado"])) if delegados[1]["nomDelegado"] != None else "")

                self.btnD1.setEnabled(bool(self.btnD1.text()))
                self.btnD2.setEnabled(bool(self.btnD2.text()))

                self.btnD1.clicked.connect(lambda: (self.btnD1.setStyleSheet(colores[1]), self.btnD2.setStyleSheet(colores[0]), setattr(self, "delegado", self.btnD1.text())))
                self.btnD2.clicked.connect(lambda: (self.btnD2.setStyleSheet(colores[1]), self.btnD1.setStyleSheet(colores[0]), setattr(self, "delegado", self.btnD2.text())))
                if self.btnD1.isEnabled() and not self.btnD2.isEnabled():
                    self.btnD1.click()
                if self.btnD2.isEnabled() and not self.btnD1.isEnabled():
                    self.btnD2.click()

                self.btnAnotar.clicked.connect(lambda: AnotarObservacion(idObs=0))

            except:
                self.btnD1.setText("")
                self.btnD2.setText("")
                self.btnD1.setStyleSheet(colores[1])
                self.btnD2.setStyleSheet(colores[1])

        delegaciones = requests.get(self.SERVIDOR + "/GETpasar_codigo", json={"codigo": "SELECT nomDelegacion FROM tabDelegaciones"}).json()
        delegaciones = [fila["nomDelegacion"] for fila in delegaciones]
        self.completerDelegacion = QCompleter(delegaciones)
        self.completerDelegacion.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtDelegacion.setCompleter(self.completer)

        self.txtDelegacion.textChanged.connect(lambda: ElegirDelegado(self.txtDelegacion.text()))
        self.btnHistorialObservaciones.clicked.connect(lambda: AbrirHistorial())

    def PaisesEnForo(self):          # Actualizar que paises se cargarán, cargar la lista y checkboxes para seleccionar o no las delegaciones
        def PaisEnForo(state, pais): # Pone que una delegacion esté en el foro
            self.cursor.execute("""UPDATE tabDelegaciones SET enforo = ? WHERE nomDelegacion = ?""", (state, pais))
            self.conn.commit()
            self.cursor.execute("""INSERT INTO tabDelegados
                                (nomDelegado, idDelegacion, alumnoCEPB, idCursoSeccion)
                                SELECT NULL, tabDelegaciones.idDelegacion, NULL, NULL
                                FROM tabDelegaciones
                                WHERE tabDelegaciones.nomDelegacion = ?
                                AND NOT EXISTS (
                                    SELECT *
                                    FROM tabDelegados
                                    WHERE tabDelegaciones.idDelegacion = tabDelegados.idDelegacion)

                                UNION ALL

                                SELECT NULL, tabDelegaciones.idDelegacion, NULL, NULL
                                FROM tabDelegaciones
                                WHERE tabDelegaciones.nomDelegacion = ?
                                AND NOT EXISTS (
                                    SELECT *
                                    FROM tabDelegados
                                    WHERE tabDelegados.idDelegacion = tabDelegaciones.idDelegacion);""", (pais, pais))
            self.conn.commit()
            self.Buscador()
        def BuscarPais(n):          # Este actualiza el buscador de paises en la fila principal
            self.listaForo.setRowCount(0)
            self.cursor.execute("""SELECT * FROM tabDelegaciones WHERE nomDelegacion LIKE ?""", (f"{n}%",))          #load bearing porcentaje
            for fila in self.cursor.fetchall():
                pais = fila["nomDelegacion"]
                btn_paisEnForo = QCheckBox()
                btn_paisEnForo.setChecked(bool(fila["enforo"]))
                btn_paisEnForo.stateChanged.connect(lambda state, p=pais: PaisEnForo(state, p))
                btn_paisEnForo.setLayoutDirection(Qt.RightToLeft)

                row_position = self.listaForo.rowCount()
                self.listaForo.insertRow(row_position)
                self.listaForo.setItem(row_position,0,QTableWidgetItem(fila["nomDelegacion"]))
                self.listaForo.setCellWidget(row_position,1,btn_paisEnForo)
        BuscarPais("")

        self.txtBuscarEnForo.textChanged.connect(BuscarPais)

    def LimpiarLayout(self,layout):  # Una cantidad sorprendente de funciones necesitan limpiar un layout   ???
            while layout.layout().count():
                item = layout.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.DelegacionesEnForo(item.layout())

    def DelegacionesEnForo(self, layout): # Nombra a los delegados en una delegación
        self.LimpiarLayout(layout)
        self.cursor.execute("""SELECT idDelegacion, nomDelegacion FROM tabDelegaciones WHERE enforo = 2""")
        paisesEnForo=self.cursor.fetchall()
        hLayout = QHBoxLayout()

        for delegacion in paisesEnForo:
            nomPais = QLabel(str(delegacion["nomDelegacion"]))
            nomPais.setStyleSheet('font: 12pt "Bahnschrift SemiBold"; text-align: center;')
            nomPais.setAlignment(Qt.AlignCenter)
            
            self.cursor.execute("""SELECT * FROM tabDelegados WHERE idDelegacion = ?""", (int(delegacion["idDelegacion"]),))
            hLayout = QHBoxLayout()
            for delegado in self.cursor.fetchall():
                Delegado = str(delegado["nomDelegado"])
                d = QLineEdit(Delegado if Delegado != "None" else "")
                d.setStyleSheet('background-color: rgb(230, 230, 230);border-radius: 5px;padding:5px;font: 12pt "Bahnschrift SemiBold"; margin-bottom: 40px;')
                d.textChanged.connect(lambda texto, idNota=delegado["idDelegado"]: 
                                      (self.cursor.execute("""UPDATE tabDelegados SET nomDelegado = ? WHERE idDelegado = ?""",(texto, idNota)),
                                       self.conn.commit()))
                hLayout.addWidget(d)

                self.conn.commit()
            layout.layout().addWidget(nomPais)
            layout.layout().addLayout(hLayout)   
            layout.layout().addStretch()

    def Cronometro(self):            # Afecta el *Cronometro*. 
        def MoverReloj(fecha):
            self.Cron.setSliderPosition(30+int(fecha.hour() * 60 + fecha.minute()))

        def IniciarCronometro(fecha):
            self.timerCron = QTimer()
            self.tiempoCron = QTime(fecha)

            def Cronometrar():
                self.tiempoCron = self.tiempoCron.addSecs(-1)
                self.txtCron.setTime(self.tiempoCron)
                MoverReloj(self.tiempoCron)
                if self.tiempoCron == QTime(0, 0, 0):
                    self.timerCron.stop()
                    self.txtCron.setReadOnly(False)
                    self.Expandir(self.Cronometro_2)

            self.txtCron.setReadOnly(True)
            self.timerCron.timeout.connect(Cronometrar)
            self.timerCron.start(1000)

        self.txtCron.timeChanged.connect(MoverReloj)
        self.btnComenzarCron.clicked.connect(lambda:(IniciarCronometro(self.txtCron.time()), MoverReloj(self.txtCron.time())))
        self.btnPausarCron.clicked.connect(lambda: (self.txtCron.setReadOnly(True if not self.txtCron.isReadOnly() else False), self.timerCron.stop()))

    def Configuraciones(self):       # Permite cambiar los tiempos
        def CambiarTiempo(columna, tiempo):
            segundos = tiempo.hour()*3600 + tiempo.minute()*60 + tiempo.second()
            self.cursor.execute(f"UPDATE tabTiempos SET {columna} = ?", (segundos,))
            self.conn.commit()

        self.cursor.execute("SELECT leer, cuestionar, pensar, contestar FROM tabTiempos")
        tLectura, tCuestionar, tPensar, tContestar = self.cursor.fetchone()

        self.timeLectura.setTime(self.timeLectura.time().addSecs(tLectura))
        self.timeCuestionar.setTime(self.timeCuestionar.time().addSecs(tCuestionar))
        self.timePensar.setTime(self.timePensar.time().addSecs(tPensar))
        self.timeContestar.setTime(self.timeContestar.time().addSecs(tContestar))

        self.timeLectura.timeChanged.connect(lambda t: CambiarTiempo("leer", t))
        self.timeCuestionar.timeChanged.connect(lambda t: CambiarTiempo("cuestionar", t))
        self.timePensar.timeChanged.connect(lambda t: CambiarTiempo("pensar", t))
        self.timeContestar.timeChanged.connect(lambda t: CambiarTiempo("contestar", t))

        self.btn_verPaises.clicked.connect(lambda _, c=self.listaPaises_2: self.Expandir(c))
        self.btn_nombrarPaises.clicked.connect(lambda _, c=self.Delegados_3: (self.Expandir(c), self.DelegacionesEnForo(self.Delegados)))
        self.nombrarMesa1 = NombrarMesa(1)
        self.nombrarMesa1.setModal(True)
        self.btn_nombrarMesa.clicked.connect(lambda: self.nombrarMesa1.show())

    def Expandir(self, nombre):      #Expandir la barra al costado, comprimir las demas barras
        self.sideBar.setMaximumWidth(400)
        self.Anotaciones_2.setMaximumHeight(0)
        self.Configuraciones_2.setMaximumHeight(0)
        self.Historial.setMaximumHeight(0)
        self.Cronometro_2.setMaximumHeight(0)
        self.listaPaises_2.setMaximumHeight(0)
        self.Delegados_3.setMaximumHeight(0)
        nombre.setMaximumHeight(16777215)
    
    # def closeEvent(self, a0):        #Reiniciar los turnos de las delegaciones al cerrar el programa, crear un pdf que registra lo que sucedió en la sesión
    #     self.cursor.execute("""UPDATE tabDelegaciones SET turnos = 0""")
    #     self.conn.commit()
    #     self.conn.close()

app= QApplication(sys.argv)
ventana= CEPBMOON()
ventana.show()
sys.exit(app.exec_()) 