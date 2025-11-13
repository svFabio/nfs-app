**Pendiente**
Planear el deploy para remotas (ejecutable?)


**Requisitos**

Sistema Operativo: openSUSE Leap 15.6
Python: 3.11.x
PyQt6: 6.6.x

servidor NFS
```
sudo zypper install nfs-kernel-server
```

**Instalar dependencias**
```
sudo zypper install python311-PyQt6
```

**Ejecucion**
```
python3.11 -m nfs_app.main
```

**Estructura del proyecto**
```
nfs-app/
├── README.md
└── nfs_app/
   ├── __init__.py
   ├── main.py
   ├── main_window.py
   ├── dialogs.py
   └── exports_parser.py
