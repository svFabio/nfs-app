# nfs_app/dialogs.py
"""
Diálogos simples siguiendo el diseño de YaST.
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDialogButtonBox, QPushButton, QFileDialog, QFormLayout
)


class AddDirectoryDialog(QDialog):
    """
    Diálogo para añadir/editar un directorio.
    Tiene un campo de texto y un botón Browse.
    """
    def __init__(self, parent=None, directorio_actual=""):
        super().__init__(parent)
        self.setWindowTitle("Directory to Export")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Campo de entrada + botón Browse
        form_layout = QFormLayout()

        input_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(directorio_actual)
        self.path_input.setPlaceholderText("/srv/nfs_share")

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.abrir_explorador)

        input_layout.addWidget(self.path_input)
        input_layout.addWidget(browse_btn)

        form_layout.addRow("", input_layout)
        layout.addLayout(form_layout)

        # Botones OK/Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def abrir_explorador(self):
        """Abre el explorador de carpetas."""
        directorio = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.path_input.text() or os.path.expanduser("~")
        )
        if directorio:
            self.path_input.setText(directorio)

    def get_path(self):
        """Devuelve la ruta introducida."""
        return self.path_input.text().strip()


class AddHostDialog(QDialog):
    """
    Diálogo para añadir/editar un host.
    Solo tiene 2 campos de texto: Host y Options.
    """
    def __init__(self, parent=None, host_actual="", opciones_actuales=""):
        super().__init__(parent)
        self.setWindowTitle("Host Wild Card")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Formulario simple con 2 campos
        form_layout = QFormLayout()

        self.host_input = QLineEdit()
        self.host_input.setText(host_actual)
        self.host_input.setPlaceholderText("192.168.1.0/24, *.example.com, or *")

        self.options_input = QLineEdit()
        self.options_input.setText(opciones_actuales)
        self.options_input.setPlaceholderText("rw,sync,no_subtree_check")

        form_layout.addRow("Host Wild Card:", self.host_input)
        form_layout.addRow("Options:", self.options_input)

        layout.addLayout(form_layout)

        # Botones OK/Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_host_options(self):
        """Devuelve (host, opciones)."""
        host = self.host_input.text().strip() or "*"
        options = self.options_input.text().strip() or "ro,sync,root_squash"
        return (host, options)
