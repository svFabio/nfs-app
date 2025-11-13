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
Se añaden instrucciones para ejecutar la app con sudo preservando las variables de entorno actuales. Esto es necesario porque:

1. PYTHONPATH: Root necesita saber dónde está el módulo 'nfs_app'.
2. DISPLAY & XAUTHORITY: Root necesita acceso a la sesión gráfica del usuario para dibujar la ventana.

**Ejecucion**
```
sudo env PYTHONPATH=$(pwd) DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY python3.11 -m nfs_app.main
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
