# nfs_app/main_window.py
"""
Ventana principal de la aplicación NFS.
"""
import os
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt

from .dialogs import AddDirectoryDialog, AddHostDialog
from .exports_parser import parsear_exports, escribir_exports, recargar_exportfs, verificar_permisos


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()


        self.exports_data = {}

        self.setWindowTitle("Directorios para Exportar")
        self.setGeometry(100, 100, 900, 600)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QVBoxLayout()


        grupo_dirs = QGroupBox("Directorios")
        layout_dirs = QVBoxLayout()

        self.lista_directorios = QListWidget()
        self.lista_directorios.currentItemChanged.connect(self.actualizar_lista_hosts)
        layout_dirs.addWidget(self.lista_directorios)


        btns_dirs = QHBoxLayout()
        btns_dirs.addStretch()

        self.btn_add_dir = QPushButton("Agregar Directorio")
        self.btn_add_dir.clicked.connect(self.add_directory)

        self.btn_edit_dir = QPushButton("Editar")
        self.btn_edit_dir.clicked.connect(self.edit_directory)
        self.btn_edit_dir.setEnabled(False)

        self.btn_delete_dir = QPushButton("Eliminar")
        self.btn_delete_dir.clicked.connect(self.delete_directory)
        self.btn_delete_dir.setEnabled(False)

        btns_dirs.addWidget(self.btn_add_dir)
        btns_dirs.addWidget(self.btn_edit_dir)
        btns_dirs.addWidget(self.btn_delete_dir)

        layout_dirs.addLayout(btns_dirs)
        grupo_dirs.setLayout(layout_dirs)

        layout_principal.addWidget(grupo_dirs)


        label_directorio_sel = QLabel()
        label_directorio_sel.setText("")
        self.label_directorio_sel = label_directorio_sel

        grupo_hosts = QGroupBox()
        layout_hosts = QVBoxLayout()


        tabs_layout = QHBoxLayout()
        tabs_layout.addWidget(QLabel("Host panel"))
        tabs_layout.addWidget(QLabel("Opciones"))
        tabs_layout.addStretch()
        layout_hosts.addLayout(tabs_layout)


        self.tabla_hosts = QTableWidget()
        self.tabla_hosts.setColumnCount(2)
        self.tabla_hosts.setHorizontalHeaderLabels(["Host panel", "Opciones"])
        self.tabla_hosts.horizontalHeader().setStretchLastSection(True)
        self.tabla_hosts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_hosts.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_hosts.itemSelectionChanged.connect(self.actualizar_botones_hosts)

        layout_hosts.addWidget(self.tabla_hosts)


        btns_hosts = QHBoxLayout()
        btns_hosts.addStretch()

        self.btn_add_host = QPushButton("Aniadir Host")
        self.btn_add_host.clicked.connect(self.add_host)
        self.btn_add_host.setEnabled(False)

        self.btn_edit_host = QPushButton("Editar")
        self.btn_edit_host.clicked.connect(self.edit_host)
        self.btn_edit_host.setEnabled(False)

        self.btn_delete_host = QPushButton("Borrar")
        self.btn_delete_host.clicked.connect(self.delete_host)
        self.btn_delete_host.setEnabled(False)

        btns_hosts.addWidget(self.btn_add_host)
        btns_hosts.addWidget(self.btn_edit_host)
        btns_hosts.addWidget(self.btn_delete_host)

        layout_hosts.addLayout(btns_hosts)
        grupo_hosts.setLayout(layout_hosts)

        layout_principal.addWidget(grupo_hosts)


        btns_finales = QHBoxLayout()
        btns_finales.addWidget(QPushButton("Ayuda"))
        btns_finales.addStretch()
        btns_finales.addWidget(QPushButton("Atras"))

        btn_finish = QPushButton("Terminado")
        btn_finish.clicked.connect(self.guardar_y_salir)
        btns_finales.addWidget(btn_finish)

        layout_principal.addLayout(btns_finales)
        central_widget.setLayout(layout_principal)


        self.cargar_exports_real()



    def cargar_exports_real(self):

        try:
            self.exports_data = parsear_exports()
            self.actualizar_lista_directorios()
            print(f"✓ Cargados {len(self.exports_data)} directorios desde /etc/exports")
        except PermissionError:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No se puede leer /etc/exports.\n\n"
                "Ejecuta la aplicación con sudo:\n"
                "sudo python3.11 -m nfs_app.main"
            )

            self.exports_data = {}
            self.actualizar_lista_directorios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al leer /etc/exports:\n{e}")
            self.exports_data = {}
            self.actualizar_lista_directorios()

    def actualizar_lista_directorios(self):

        seleccion_actual = self.lista_directorios.currentItem()
        ruta_seleccionada = seleccion_actual.text() if seleccion_actual else None

        self.lista_directorios.clear()
        self.lista_directorios.addItems(self.exports_data.keys())


        if ruta_seleccionada and ruta_seleccionada in self.exports_data:
            items = self.lista_directorios.findItems(ruta_seleccionada, Qt.MatchFlag.MatchExactly)
            if items:
                self.lista_directorios.setCurrentItem(items[0])


        tiene_seleccion = self.lista_directorios.currentItem() is not None
        self.btn_edit_dir.setEnabled(tiene_seleccion)
        self.btn_delete_dir.setEnabled(tiene_seleccion)

    def add_directory(self):

        dialog = AddDirectoryDialog(self)
        if dialog.exec():
            ruta = dialog.get_path()
            if not ruta:
                return


            if not os.path.exists(ruta):
                reply = QMessageBox.question(
                    self,
                    "MiniYaST2",
                    f"El directorio no existe. Desea crearlo?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        os.makedirs(ruta)
                    except PermissionError:
                        QMessageBox.critical(self, "Error", "Permiso denegado.\nIntenta como root.")
                        return
                else:

                    return




            try:

                subprocess.run(["chown", "nobody:nobody", ruta], check=True)


                subprocess.run(["chmod", "775", ruta], check=True)

            except Exception as e:
                QMessageBox.critical(self, "Error de Permisos", f"No se pudo preparar la carpeta '{ruta}'.\nError: {e}")
                return



            if ruta not in self.exports_data:
                self.exports_data[ruta] = []
                self.actualizar_lista_directorios()

                items = self.lista_directorios.findItems(ruta, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lista_directorios.setCurrentItem(items[0])

    def edit_directory(self):

        item = self.lista_directorios.currentItem()
        if not item:
            return

        ruta_vieja = item.text()
        dialog = AddDirectoryDialog(self, ruta_vieja)
        if dialog.exec():
            ruta_nueva = dialog.get_path()
            if not ruta_nueva or ruta_nueva == ruta_vieja:
                return


            if ruta_nueva not in self.exports_data:
                self.exports_data[ruta_nueva] = self.exports_data.pop(ruta_vieja)
                self.actualizar_lista_directorios()

                items = self.lista_directorios.findItems(ruta_nueva, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lista_directorios.setCurrentItem(items[0])

    def delete_directory(self):

        item = self.lista_directorios.currentItem()
        if not item:
            return

        ruta = item.text()
        reply = QMessageBox.question(
            self, "Confirmar",
            f"Eliminar directorio '{ruta}' de exports?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.exports_data[ruta]
            self.actualizar_lista_directorios()



    def actualizar_lista_hosts(self, current_item, previous_item):

        self.tabla_hosts.setRowCount(0)

        if not current_item:
            self.btn_add_host.setEnabled(False)
            self.btn_edit_host.setEnabled(False)
            self.btn_delete_host.setEnabled(False)
            return

        directorio = current_item.text()
        self.btn_add_host.setEnabled(True)

        hosts = self.exports_data.get(directorio, [])
        self.tabla_hosts.setRowCount(len(hosts))

        for i, (host, opts) in enumerate(hosts):
            self.tabla_hosts.setItem(i, 0, QTableWidgetItem(host))
            self.tabla_hosts.setItem(i, 1, QTableWidgetItem(opts))

    def actualizar_botones_hosts(self):

        tiene_seleccion = len(self.tabla_hosts.selectedItems()) > 0
        self.btn_edit_host.setEnabled(tiene_seleccion)
        self.btn_delete_host.setEnabled(tiene_seleccion)

    def add_host(self):

        item = self.lista_directorios.currentItem()
        if not item:
            return

        directorio = item.text()
        dialog = AddHostDialog(self)
        if dialog.exec():
            host, opts = dialog.get_host_options()
            self.exports_data[directorio].append((host, opts))
            self.actualizar_lista_hosts(item, None)

    def edit_host(self):

        fila = self.tabla_hosts.currentRow()
        if fila < 0:
            return

        item_dir = self.lista_directorios.currentItem()
        if not item_dir:
            return

        directorio = item_dir.text()
        host_viejo, opts_viejas = self.exports_data[directorio][fila]

        dialog = AddHostDialog(self, host_viejo, opts_viejas)
        if dialog.exec():
            host_nuevo, opts_nuevas = dialog.get_host_options()
            self.exports_data[directorio][fila] = (host_nuevo, opts_nuevas)
            self.actualizar_lista_hosts(item_dir, None)

    def delete_host(self):

        fila = self.tabla_hosts.currentRow()
        if fila < 0:
            return

        item_dir = self.lista_directorios.currentItem()
        if not item_dir:
            return

        directorio = item_dir.text()
        reply = QMessageBox.question(
            self, "Confirmar",
            "Eliminar hosts seleccionados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.exports_data[directorio][fila]
            self.actualizar_lista_hosts(item_dir, None)



    def guardar_y_salir(self):

        if not verificar_permisos():
            QMessageBox.critical(
                self,
                "Error de permisos",
                "No tienes permisos para escribir en /etc/exports.\n\n"
                "Ejecuta la aplicación con sudo:\n"
                "sudo python3.11 -m nfs_app.main"
            )
            return

        try:

            escribir_exports(self.exports_data)


            recargar_exportfs()

            QMessageBox.information(
                self,
                "Éxito",
                "Configuración guardada en /etc/exports\n"
                "Servidor NFS recargado correctamente."
            )

        except PermissionError as e:
            QMessageBox.critical(self, "Error de permisos", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")
