# nfs_app/main_window.py
"""
Ventana principal de la aplicación NFS.
Replica exactamente el diseño de YaST.
"""
import os
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

        # Modelo de datos: { "/ruta/dir": [ ("host1", "opts1"), ("host2", "opts2") ] }
        self.exports_data = {}

        self.setWindowTitle("Directories to Export")
        self.setGeometry(100, 100, 900, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QVBoxLayout()

        # --- SECCIÓN 1: DIRECTORIOS ---
        grupo_dirs = QGroupBox("Directories")
        layout_dirs = QVBoxLayout()

        self.lista_directorios = QListWidget()
        self.lista_directorios.currentItemChanged.connect(self.actualizar_lista_hosts)
        layout_dirs.addWidget(self.lista_directorios)

        # Botones de directorios
        btns_dirs = QHBoxLayout()
        btns_dirs.addStretch()

        self.btn_add_dir = QPushButton("Add Directory")
        self.btn_add_dir.clicked.connect(self.add_directory)

        self.btn_edit_dir = QPushButton("Edit")
        self.btn_edit_dir.clicked.connect(self.edit_directory)
        self.btn_edit_dir.setEnabled(False)

        self.btn_delete_dir = QPushButton("Delete")
        self.btn_delete_dir.clicked.connect(self.delete_directory)
        self.btn_delete_dir.setEnabled(False)

        btns_dirs.addWidget(self.btn_add_dir)
        btns_dirs.addWidget(self.btn_edit_dir)
        btns_dirs.addWidget(self.btn_delete_dir)

        layout_dirs.addLayout(btns_dirs)
        grupo_dirs.setLayout(layout_dirs)

        layout_principal.addWidget(grupo_dirs)

        # --- SECCIÓN 2: HOSTS (con pestañas visuales) ---
        # Label que simula las pestañas de YaST
        label_directorio_sel = QLabel()
        label_directorio_sel.setText("")  # Se actualizará dinámicamente
        self.label_directorio_sel = label_directorio_sel

        grupo_hosts = QGroupBox()
        layout_hosts = QVBoxLayout()

        # Pestañas falsas (solo visual)
        tabs_layout = QHBoxLayout()
        tabs_layout.addWidget(QLabel("Host Wild Card"))
        tabs_layout.addWidget(QLabel("Options"))
        tabs_layout.addStretch()
        layout_hosts.addLayout(tabs_layout)

        # TABLA con 2 columnas (Host | Options)
        self.tabla_hosts = QTableWidget()
        self.tabla_hosts.setColumnCount(2)
        self.tabla_hosts.setHorizontalHeaderLabels(["Host Wild Card", "Options"])
        self.tabla_hosts.horizontalHeader().setStretchLastSection(True)
        self.tabla_hosts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_hosts.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_hosts.itemSelectionChanged.connect(self.actualizar_botones_hosts)

        layout_hosts.addWidget(self.tabla_hosts)

        # Botones de hosts
        btns_hosts = QHBoxLayout()
        btns_hosts.addStretch()

        self.btn_add_host = QPushButton("Add Host")
        self.btn_add_host.clicked.connect(self.add_host)
        self.btn_add_host.setEnabled(False)

        self.btn_edit_host = QPushButton("Edit")
        self.btn_edit_host.clicked.connect(self.edit_host)
        self.btn_edit_host.setEnabled(False)

        self.btn_delete_host = QPushButton("Delete")
        self.btn_delete_host.clicked.connect(self.delete_host)
        self.btn_delete_host.setEnabled(False)

        btns_hosts.addWidget(self.btn_add_host)
        btns_hosts.addWidget(self.btn_edit_host)
        btns_hosts.addWidget(self.btn_delete_host)

        layout_hosts.addLayout(btns_hosts)
        grupo_hosts.setLayout(layout_hosts)

        layout_principal.addWidget(grupo_hosts)

        # --- BOTONES FINALES ---
        btns_finales = QHBoxLayout()
        btns_finales.addWidget(QPushButton("Help"))
        btns_finales.addStretch()
        btns_finales.addWidget(QPushButton("Back"))

        btn_finish = QPushButton("Finish")
        btn_finish.clicked.connect(self.guardar_y_salir)
        btns_finales.addWidget(btn_finish)

        layout_principal.addLayout(btns_finales)
        central_widget.setLayout(layout_principal)

        # Cargar datos REALES de /etc/exports
        self.cargar_exports_real()

    # --- GESTIÓN DE DIRECTORIOS ---

    def cargar_exports_real(self):
        """Lee el archivo /etc/exports REAL y carga los datos."""
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
            # Cargar vacío si no hay permisos
            self.exports_data = {}
            self.actualizar_lista_directorios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al leer /etc/exports:\n{e}")
            self.exports_data = {}
            self.actualizar_lista_directorios()

    def actualizar_lista_directorios(self):
        """Refresca la lista de directorios."""
        seleccion_actual = self.lista_directorios.currentItem()
        ruta_seleccionada = seleccion_actual.text() if seleccion_actual else None

        self.lista_directorios.clear()
        self.lista_directorios.addItems(self.exports_data.keys())

        # Restaurar selección si existía
        if ruta_seleccionada and ruta_seleccionada in self.exports_data:
            items = self.lista_directorios.findItems(ruta_seleccionada, Qt.MatchFlag.MatchExactly)
            if items:
                self.lista_directorios.setCurrentItem(items[0])

        # Habilitar/deshabilitar botones según si hay algo SELECCIONADO
        tiene_seleccion = self.lista_directorios.currentItem() is not None
        self.btn_edit_dir.setEnabled(tiene_seleccion)
        self.btn_delete_dir.setEnabled(tiene_seleccion)

    def add_directory(self):
        """Añadir un nuevo directorio."""
        dialog = AddDirectoryDialog(self)
        if dialog.exec():
            ruta = dialog.get_path()
            if not ruta:
                return

            # Verificar si existe
            if not os.path.exists(ruta):
                reply = QMessageBox.question(
                    self,
                    "YaST2",
                    f"The directory does not exist. Create it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        os.makedirs(ruta)
                    except PermissionError:
                        QMessageBox.critical(self, "Error", "Permission denied.\nRun as root.")
                        return
                else:
                    return

            # Añadir al modelo
            if ruta not in self.exports_data:
                self.exports_data[ruta] = []
                self.actualizar_lista_directorios()
                # Seleccionarlo
                items = self.lista_directorios.findItems(ruta, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lista_directorios.setCurrentItem(items[0])

    def edit_directory(self):
        """Editar el directorio seleccionado."""
        item = self.lista_directorios.currentItem()
        if not item:
            return

        ruta_vieja = item.text()
        dialog = AddDirectoryDialog(self, ruta_vieja)
        if dialog.exec():
            ruta_nueva = dialog.get_path()
            if not ruta_nueva or ruta_nueva == ruta_vieja:
                return

            # Actualizar el modelo
            if ruta_nueva not in self.exports_data:
                self.exports_data[ruta_nueva] = self.exports_data.pop(ruta_vieja)
                self.actualizar_lista_directorios()
                # Seleccionar el nuevo
                items = self.lista_directorios.findItems(ruta_nueva, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lista_directorios.setCurrentItem(items[0])

    def delete_directory(self):
        """Eliminar el directorio seleccionado."""
        item = self.lista_directorios.currentItem()
        if not item:
            return

        ruta = item.text()
        reply = QMessageBox.question(
            self, "Confirm",
            f"Delete directory '{ruta}' from exports?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.exports_data[ruta]
            self.actualizar_lista_directorios()

    # --- GESTIÓN DE HOSTS ---

    def actualizar_lista_hosts(self, current_item, previous_item):
        """Se activa al seleccionar un directorio."""
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
        """Habilita/deshabilita botones según la selección."""
        tiene_seleccion = len(self.tabla_hosts.selectedItems()) > 0
        self.btn_edit_host.setEnabled(tiene_seleccion)
        self.btn_delete_host.setEnabled(tiene_seleccion)

    def add_host(self):
        """Añadir un host al directorio seleccionado."""
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
        """Editar el host seleccionado."""
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
        """Eliminar el host seleccionado."""
        fila = self.tabla_hosts.currentRow()
        if fila < 0:
            return

        item_dir = self.lista_directorios.currentItem()
        if not item_dir:
            return

        directorio = item_dir.text()
        reply = QMessageBox.question(
            self, "Confirm",
            "Delete selected host?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.exports_data[directorio][fila]
            self.actualizar_lista_hosts(item_dir, None)

    # --- GUARDADO FINAL ---

    def guardar_y_salir(self):
        """Guarda los cambios en /etc/exports REAL y recarga el servidor NFS."""
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
            # Guardar en /etc/exports
            escribir_exports(self.exports_data)

            # Recargar el servidor NFS
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
