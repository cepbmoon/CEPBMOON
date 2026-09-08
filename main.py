print("\33c")
from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
import sys
import socketio
from PyQt5.QtCore import pyqtSignal

SERVIDOR = "https://cepbmoon.onrender.com"
# SERVIDOR = "http://127.0.0.1:5000"

class ConectarForo(QDialog):
    def __init__(self):
        super().__init__()
        self.SERVIDOR = SERVIDOR  #Va a ser el link a render!!
        loadUi("conectarMesa.ui", self)
        self.btnVolverCrear.clicked.connect(lambda: self.funcionquetemandadeunoaotro(self.wgtCrear))
        self.btnVolverIniciar.clicked.connect(lambda: self.funcionquetemandadeunoaotro(self.wgtIngresar))

        self.btnIniciarSesion.clicked.connect(self.IniciarSesion)
        self.btnCrearSesion.clicked.connect(self.CrearSesion)

        self.idSesion=0

    def funcionquetemandadeunoaotro(self, nombre):
        self.wgtCrear.setMaximumWidth(0)
        self.wgtCrear.setEnabled(False)
        self.wgtIngresar.setMaximumWidth(0)
        self.wgtIngresar.setEnabled(False)
        nombre.setMaximumWidth(16777215)
        nombre.setEnabled(True)
        
    def CrearSesion(self):
        if self.txtCodigoCREAR.text() != self.txtConfCodigo.text():
            self.txtErrorCREAR.setText("Las contraseñas no son iguales")
        else:
            if self.txtCodigoCREAR.text() and self.txtConfCodigo.text() and self.txtNomForoCREAR.text():
                respuesta = requests.get(self.SERVIDOR + "/POSTcrearForo", json={"params": {"nomForo":self.txtNomForoCREAR.text().upper(), "contraseña": self.txtCodigoCREAR.text()}}).json()
                try:
                    self.idSesion = int(respuesta["idSesion"])
                    self.close()
                    return self.idSesion
                except:
                    self.txtErrorCREAR.setText(respuesta["error"])
                return self.idSesion

    def IniciarSesion(self):
        respuesta = requests.get(self.SERVIDOR + "/GETingresarForo", json={"params": {"nomForo":self.txtNomForoINICIAR.text().upper() or "", "contraseña": self.txtCodigoINICIAR.text() or ""}}).json()
        try:
            self.idSesion = respuesta["idSesion"]
            self.close()
            return self.idSesion
        except:
            self.txtError.setText(respuesta["error"])

    def closeEvent(self, a0):
        if self.idSesion:
            super().closeEvent(a0)
        else:
            a0.ignore()
    
class NombrarMesa(QDialog):
    def __init__(self, msj, mesa, idSesion):
        super().__init__()
        self.SERVIDOR = SERVIDOR
        loadUi("dialog.ui", self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.mesa = mesa
        self.idSesion = idSesion
        if msj == 1:
            self.msjBienvenida.setMaximumHeight(0)

        self.btnGuardar.clicked.connect(self.GuardarNombres)
        self.Nombres()

    def Nombres(self):
        self.nomPresidente.setText(self.mesa["Presidente"] or "")
        self.nomModerador.setText(self.mesa["Moderador"] or "")
        self.nomSecretario.setText(self.mesa["Secretario"] or "")
        self.nomEvaluador.setText(self.mesa["Evaluador"] or "")
        self.ano.setText(str(self.mesa["Año"]) if self.mesa["Año"] else "")

    def GuardarNombres(self):
        presidente = self.nomPresidente.text() or None
        moderador = self.nomModerador.text() or None
        secretario = self.nomSecretario.text() or None
        evaluador = self.nomEvaluador.text() or None
        ano = self.ano.text() or None
        requests.post(self.SERVIDOR + "/POSTmesa", json={"params": [presidente, moderador, secretario, evaluador, ano], "idSesion": self.idSesion})
        self.close()

    def closeEvent(self, a0):
        if self.nomPresidente.text():
            super().closeEvent(a0)
        else:
            a0.ignore()

class HistorialObservaciones(QMainWindow):
    def __init__(self, idSesion):
        super().__init__()
        self.SERVIDOR = SERVIDOR  #Va a ser el link a render!!
        loadUi("historialObs.ui", self)

        self.idSesion = idSesion
        self.tabHistorial.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabHistorial.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabHistorial.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        observaciones = requests.get(self.SERVIDOR + "/GETobservaciones", json={"idSesion": self.idSesion}).json()
        try:
            for observacion in observaciones:
                self.tabHistorial.insertRow(0)
                self.tabHistorial.setItem(0, 0, QTableWidgetItem(observacion["nomDelegacion"]))
                self.tabHistorial.setItem(0, 1, QTableWidgetItem(observacion["nomDelegado"]))
                self.tabHistorial.setItem(0, 2, QTableWidgetItem(observacion["descObs"]))
                self.tabHistorial.setItem(0, 3, QTableWidgetItem(str(observacion["puntaje"])))
        except:
            pass

class imgButton(QPushButton):
    def __init__(self, img, text, parent):
        super(imgButton, self).__init__(parent)
        layout = QVBoxLayout(self)

        icon = QIcon(img)
        pixmap = icon.pixmap(75, 150, QIcon.Active, QIcon.On)
        self.bandera = QLabel(self)
        self.bandera.setPixmap(pixmap)
        self.bandera.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bandera) # (stretch factor 0)

        self.nomDelegacion = QLabel(text)
        self.nomDelegacion.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        self.nomDelegacion.setWordWrap(True)
        layout.addWidget(self.nomDelegacion)
        self.show()

class CEPBMOON(QMainWindow):
    cambiosRecibidos = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.SERVIDOR = SERVIDOR
        self.sio = socketio.Client()
        self.cambiosRecibidos.connect(self.ProcesarCambios)

        loadUi("main.ui", self)
        self.setEnabled(False)
        self.idSesion = 0

        self.conectarSesion = ConectarForo()
        self.conectarSesion.setModal(True)
        self.conectarSesion.finished.connect(self.ConectarFunciones)    # Se llaman todas la funciones
        self.conectarSesion.show()

        self.versionCambios = 0
        self.versionFila = 0
        self.versionHistorial = 0

    def ConectarFunciones(self):    # Conecta los botones principales con sus funciones
        self.btn1.clicked.connect(lambda _, c=self.Configuraciones_2: self.Expandir(c))
        self.btn2.clicked.connect(lambda _, c=self.Anotaciones_2: self.Expandir(c))
        self.btn3.clicked.connect(lambda _, c=self.Cronometro_2: self.Expandir(c))
        self.btn4.clicked.connect(lambda _, c=self.Historial: self.Expandir(c))

        #Ajusta el layout de la fila de delegaciones
        self.scrollLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)
        self.timer = QTimer()
  
        self.cerrarSideBar.clicked.connect(lambda: self.sideBar.setMaximumWidth(0))
        self.btnLimpiar.clicked.connect(self.LimpiarFila)
        self.listaForo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.listaHistorial.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   
        
        if self.conectarSesion.idSesion:
            self.idSesion = self.conectarSesion.idSesion
            self.setEnabled(True)

            self.CrearFila(0)
            self.CrearHistorial(0)

            self.ConectarSocket()

        self.Buscador()                                 
        self.NombrarMesaAlAbrir()                       
        self.DelegacionesEnForo()                             
        # self.DelegacionesEnForo(self.Delegados)
        self.Configuraciones()
        self.Cronometro()
        self.Observaciones()

    def LimpiarFila(self):
        self.LimpiarLayout(self.scrollLayout)
        requests.post(self.SERVIDOR + "/limpiarFila", json={"idSesion": self.idSesion})
        self.sio.emit("cambiarFila",{"idSesion": self.idSesion})

    def ConectarSocket(self):
        self.sio.on("connect", self.SocketConectado)
        self.sio.on("disconnect", self.SocketDesconectado)
        self.sio.on("cambios", self.RecibirCambios)
        self.sio.on("cuenta regresiva", self.RecibirCambios)

        self.sio.connect(self.SERVIDOR)

    def SocketConectado(self):
        self.sio.emit("unirse_sesion", {"idSesion": self.idSesion})

    def SocketDesconectado(self):
        pass

    def RecibirCambios(self, data):
        self.cambiosRecibidos.emit(data)

    def ProcesarCambios(self, data):
        if 'versionCambios' in data and int(data["versionCambios"]) != int(self.versionCambios):
            if 'fila' in data       and int(data["versionFila"])      != int(self.versionFila):
                self.CrearFila(data["fila"])
                self.versionFila = data["versionFila"]

            if 'historial' in data  and int(data["versionHistorial"]) != int(self.versionHistorial):
                self.CrearHistorial(data["historial"])
                self.versionHistorial = data["versionHistorial"]

            self.versionCambios = data["versionCambios"]

        if 'delegacion' in data:
            self.Cronometrar(data)

    def Buscador(self):              # Actualizar el buscador cuando se cambia los paises en un foro
        self.delegacionesEnElForo = requests.get(self.SERVIDOR + "/GETdelegaciones", json={"idSesion": self.idSesion}).json()
        self.delegaciones = [fila["nomDelegacion"] for fila in self.delegacionesEnElForo]
        self.completer = QCompleter(self.delegaciones)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.txtDelegacion.setCompleter(self.completer)

        self.txtBuscador.returnPressed.connect(self.Buscar)
        self.btnBuscar.clicked.connect(self.Buscar)

    def NombrarMesaAlAbrir(self):    # Abre el menú para nombrar a los miembros de la mesa, primero comprueba que esté completa paa abrirlo
        mesa = requests.get(self.SERVIDOR + "/GETmesa", json={"idSesion": self.idSesion}).json()
        if None in mesa.values():
            self.nombrarMesa = NombrarMesa(0, mesa, self.idSesion)
            self.nombrarMesa.setModal(True) 
            self.nombrarMesa.show()

    def Buscar(self):                # Para buscar un pais y que se añada a la lista de oradores
        delegacion = self.txtBuscador.text().strip()
        if not delegacion or delegacion not in self.delegacionesEnElForo:       # Termina la función si no hay una delegacion en el buscador
            return 
        for i in range(self.scrollLayout.count()):                      # Termina la función si la delegación ya está en la fila
            item = self.scrollLayout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QPushButton) and widget.text() == delegacion:
                self.txtBuscador.clear()
                return
            
        self.sio.emit("POSTfila_delegaciones", {"delegacion": delegacion, "idSesion": self.idSesion})
        self.sio.emit("cambiarFila",{"idSesion": self.idSesion})
        self.txtBuscador.clear()

    def CrearFila(self, fila):             # Actualiza la fila de delegaciones en cola
        if not fila:
            fila = requests.get(self.SERVIDOR + "/GETfila_delegaciones", json={"idSesion": self.idSesion}).json()
        self.LimpiarLayout(self.scrollLayout)
        for delegacion in fila:
            btn = imgButton(f"CEPBMOON PAISES Y DEPARTAMENTOS/{delegacion["nomDelegacion"]}.png", delegacion["nomDelegacion"], self)
            btn.setMinimumSize(100, 100)
            btn.setMaximumSize(100, 100)
            btn.setStyleSheet('font: 10pt "Bahnschrift SemiBold"; text-align: left; background-color: rgb(255, 255, 255); border-radius: 20px;')
            btn.clicked.connect(lambda _, b=btn: self.QuitarPais(b))
            self.scrollLayout.addWidget(btn, alignment=Qt.AlignTop)
        self.scrollLayout.addStretch()
                
    def QuitarPais(self, delegacion):      # Afecta el *Historial*. Quitar un pais de la lista de oradores, registrar y cronometrarlo 
        def Cronometrar(tiempo):
            self.sio.emit("conteoDelegacion",{"nomDelegacion": nomDelegacion, "tiempo": tiempo ,"idSesion": self.idSesion})
        
        def Registrar(nomDelegacion):      # Añade el pais al historial
                requests.post(self.SERVIDOR + "/POSThistorial_delegaciones", json={"idSesion": self.idSesion, "nomDelegacion":nomDelegacion})
                self.sio.emit("cambiarHistorial",{"idSesion": self.idSesion})

        nomDelegacion = delegacion.nomDelegacion.text()
        delegacion.deleteLater()
        self.sio.emit("cambiarFila",{"idSesion": self.idSesion, "delegacion": nomDelegacion})

        self.txtCronometro.setText(str(nomDelegacion))
        self.wgt_btns.setMaximumHeight(48)

        self.btnLectura.clicked.connect(lambda: Cronometrar("leer"))
        self.btnCuestionar.clicked.connect(lambda: Cronometrar("cuestionar"))
        self.btnContestar.clicked.connect(lambda: Cronometrar("pensar"))

        Registrar(nomDelegacion)

    def Cronometrar(self, data):     # Inicia el cronómetro para las delegaciones

        nomDelegacion = data["delegacion"]
        tiempo = data["tiempo"]
        def Cronometro(pais):
            if self.time == QTime(0, 0, 0):
                self.timer.stop()
                if tiempo == "pensar":
                    self.Cronometrar("contestar")
                else:
                    self.txtCronometro.setText(f"00:00")
                return
            
            self.time = self.time.addSecs(-1)
            timeDisplay = self.time.toString("mm:ss")
            self.txtCronometro.setText(f"{timeDisplay} - {pais}")
        self.wgt_btns.setMaximumHeight(0)
        
        t = requests.get(self.SERVIDOR + "/GETtiempos", json={"idSesion": self.idSesion}).json()

        self.time = QTime(0, 0, 0)
        self.time = self.time.addSecs(int(t[f"{tiempo}"]))
        self.txtCronometro.setText(f"{self.time.toString("mm:ss")} - {str(nomDelegacion)}")
        try:
            self.timer.timeout.disconnect()
        except:
            pass
        self.timer.timeout.connect(lambda: Cronometro(nomDelegacion))
        self.timer.start(1000)

    def CrearHistorial(self, historial):        # 
        if not historial:
            historial = requests.get(self.SERVIDOR + "/GEThistorial", json={"idSesion": self.idSesion}).json()
        self.listaHistorial.clearContents()
        for delegacion in historial:
            self.listaHistorial.insertRow(0)
            self.listaHistorial.setItem(0, 0, QTableWidgetItem(delegacion["nomDelegacion"]))
            self.listaHistorial.setItem(0, 1, QTableWidgetItem(str(delegacion["turnos"])))

    def Observaciones(self):         # Agenda las observaciones
        delegadosTotal = requests.get(self.SERVIDOR + "/GETdelegados", json={"idSesion": self.idSesion}).json()
        def AbrirHistorial():                   # Abre el historial de observaciones
            self.verObservaciones = HistorialObservaciones(self.idSesion)
            self.verObservaciones.show()

        def AnotarObservacion(idObs):     # Añade la observación a la base de datos, reinicia el menú
            if self.delegado:
                params = [idObs, self.txtObservacion.toPlainText(), self.numPuntaje.text(), self.delegado]
                requests.post(self.SERVIDOR + "/POSTobservacion", json={"params": params, "idSesion": self.idSesion})
                self.delegado=""
                self.txtDelegacion.setText(self.txtObservacion.setText(""))
                self.numPuntaje.setValue(0)
        def ElegirDelegado(delegacion):               # Selecciona bajo que delegado se guardará la observación
            colores = ["background-color: rgb(156, 152, 181);border-radius: 15px;font: 11pt 'Bahnschrift SemiLight';", "background-color: rgb(186, 182, 209);border-radius: 15px;font: 11pt 'Bahnschrift SemiLight'"]
            try:
                delegados = [d for d in delegadosTotal if d.get("nomDelegacion") == delegacion]

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

        self.completerDelegacion = QCompleter(self.delegaciones)
        self.completerDelegacion.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtDelegacion.setCompleter(self.completer)

        self.txtDelegacion.textChanged.connect(lambda: ElegirDelegado(self.txtDelegacion.text()))
        self.btnHistorialObservaciones.clicked.connect(lambda: AbrirHistorial())

    def DelegacionesEnForo(self):          # Actualizar que delegaciones se cargarán, cargar la lista y checkboxes para seleccionar o no las delegaciones
        delegacionesTot = self.delegacionesEnElForo
        delegaciones = [{"nomDelegacion":d["nomDelegacion"], "idSesion": d["idSesion"]} for d in delegacionesTot]
        def DelegacionEnForo(state, delegacion): # Pone que una delegacion esté en el foro
            requests.post(self.SERVIDOR + "/POSTdelegados", json={"idSesion": self.idSesion if state else 0, "delegacion": delegacion})
            self.Buscador()

        def BuscarPais(n):          # Este actualiza el buscador de delegaciones en la fila principal
            self.listaForo.setRowCount(0)
            deles = [(d["nomDelegacion"], d["idSesion"]) for d in delegaciones if d["nomDelegacion"].lower().startswith(n.lower())]
            for nombre, id_sesion in deles:
                btn_delegacionEnForo = QCheckBox()
                btn_delegacionEnForo.setChecked(id_sesion ==self.idSesion)
                btn_delegacionEnForo.stateChanged.connect(lambda state, d=nombre: DelegacionEnForo(state, d))
                btn_delegacionEnForo.setLayoutDirection(Qt.RightToLeft)

                row_position = self.listaForo.rowCount()
                self.listaForo.insertRow(row_position)
                self.listaForo.setItem(row_position,0,QTableWidgetItem(nombre))
                self.listaForo.setCellWidget(row_position,1,btn_delegacionEnForo)
        BuscarPais("")

        self.txtBuscarEnForo.textChanged.connect(BuscarPais)

    def LimpiarLayout(self,layout):  # Una cantidad sorprendente de funciones necesitan limpiar un layout   ???
            while layout.layout().count():
                item = layout.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.DelegadosEnForo(item.layout())

    def DelegadosEnForo(self, layout): # Nombra a los delegados en una delegación
        self.LimpiarLayout(layout)
        delegacionesTot = requests.get(self.SERVIDOR + "/GETdelegaciones").json()
        delegadosTot = requests.get(self.SERVIDOR + "/GETdelegados").json()
        delegacionesEnForo = [{"nomDelegacion":d["nomDelegacion"], "idSesion":d["idSesion"], "idDelegacion":d["idDelegacion"]} for d in delegacionesTot if d["idSesion"] == self.idSesion]
        hLayout = QHBoxLayout()

        for delegacion in delegacionesEnForo:
            nomDelegacion = QLabel(str(delegacion["nomDelegacion"]))
            nomDelegacion.setStyleSheet('font: 12pt "Bahnschrift SemiBold"; text-align: center;')
            nomDelegacion.setAlignment(Qt.AlignCenter)
            
            delegados = [{"nomDelegado": ds["nomDelegado"], "idDelegado": ds["idDelegado"]} for ds in delegadosTot if ds["idDelegacion"] == delegacion["idDelegacion"]]
            hLayout = QHBoxLayout()
            for delegado in delegados:
                Delegado = str(delegado["nomDelegado"])
                dls = QLineEdit(Delegado if Delegado != "None" else "")
                dls.setStyleSheet('background-color: rgb(186, 182, 209);border-radius: 5px;padding:5px;font: 12pt "Bahnschrift SemiBold"; margin-bottom: 40px;')
                dls.textChanged.connect(lambda texto, id_del=delegado["idDelegado"]: 
                        self.sio.emit("POSTnomDelegados", {"nombre": texto, "idDelegado": id_del}))
                hLayout.addWidget(dls)
            
            layout.layout().addWidget(nomDelegacion)
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
            requests.post(self.SERVIDOR + "/POSTtiempos", json={"columna": columna, "segundos": segundos, "idSesion": self.idSesion}) 
        tLectura, tCuestionar, tPensar, tContestar = (requests.get(self.SERVIDOR + "/GETtiempos", json={"idSesion": self.idSesion}).json()).values()

        self.timeLectura.setTime(self.timeLectura.time().addSecs(tLectura))
        self.timeCuestionar.setTime(self.timeCuestionar.time().addSecs(tCuestionar))
        self.timePensar.setTime(self.timePensar.time().addSecs(tPensar))
        self.timeContestar.setTime(self.timeContestar.time().addSecs(tContestar))

        self.timeLectura.timeChanged.connect(lambda t: CambiarTiempo("leer", t))
        self.timeCuestionar.timeChanged.connect(lambda t: CambiarTiempo("cuestionar", t))
        self.timePensar.timeChanged.connect(lambda t: CambiarTiempo("pensar", t))
        self.timeContestar.timeChanged.connect(lambda t: CambiarTiempo("contestar", t))

        self.btn_verPaises.clicked.connect(lambda _, c=self.listaPaises_2: self.Expandir(c))
        self.btn_nombrarPaises.clicked.connect(lambda _, c=self.Delegados_3: (self.Expandir(c), self.DelegadosEnForo(self.Delegados)))

        self.conectarSesion = ConectarForo()
        self.conectarSesion.setModal(True)
        self.btn_conectarMesa.clicked.connect(lambda: self.conectarSesion.show())

        self.nombrarMesa1 = NombrarMesa(1, requests.get(self.SERVIDOR + "/GETmesa", json={"idSesion": self.idSesion}).json(), self.idSesion)
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

app= QApplication(sys.argv)
ventana= CEPBMOON()
ventana.show()
sys.exit(app.exec_()) 