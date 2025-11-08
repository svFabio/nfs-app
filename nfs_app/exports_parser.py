# nfs_app/exports_parser.py
"""
Funciones para leer y escribir el archivo /etc/exports.
"""
import os
import re
import subprocess
from datetime import datetime


EXPORTS_FILE = "/etc/exports"
EXPORTS_BACKUP = "/etc/exports.backup"


def parsear_exports(archivo=EXPORTS_FILE):
    """
    Lee y parsea el archivo /etc/exports.

    Retorna un diccionario:
    {
        "/ruta/directorio": [("host1", "opciones1"), ("host2", "opciones2")],
        ...
    }
    """
    if not os.path.exists(archivo):
        return {}

    exports_data = {}

    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()

                # Ignorar líneas vacías y comentarios
                if not linea or linea.startswith('#'):
                    continue

                # Parsear la línea
                # Formato: /directorio host1(opts1) host2(opts2) ...
                partes = linea.split()
                if len(partes) < 2:
                    continue  # Línea inválida

                directorio = partes[0]
                hosts = []

                # Procesar cada host(opciones)
                for host_opts in partes[1:]:
                    # Usar regex para separar host de opciones
                    # Ejemplos: "192.168.1.202(ro)", "*(rw,sync)", "192.168.1.0/24(rw)"
                    match = re.match(r'^([^\(]+)\(([^\)]*)\)$', host_opts)
                    if match:
                        host = match.group(1)
                        opciones = match.group(2)
                        hosts.append((host, opciones))
                    else:
                        # Si no tiene paréntesis, asumir opciones por defecto
                        hosts.append((host_opts, "ro,sync,root_squash"))

                if directorio and hosts:
                    exports_data[directorio] = hosts

    except PermissionError:
        raise PermissionError("No se puede leer /etc/exports. Ejecuta como root (sudo).")
    except Exception as e:
        raise Exception(f"Error al leer {archivo}: {e}")

    return exports_data


def escribir_exports(exports_data, archivo=EXPORTS_FILE, hacer_backup=True):
    """
    Escribe el diccionario exports_data en /etc/exports.

    Args:
        exports_data: Diccionario con formato { "/dir": [("host", "opts"), ...] }
        archivo: Ruta del archivo (por defecto /etc/exports)
        hacer_backup: Si True, crea una copia de seguridad antes de escribir
    """
    try:
        # Hacer backup del archivo original
        if hacer_backup and os.path.exists(archivo):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{archivo}.backup.{timestamp}"
            subprocess.run(["cp", archivo, backup_file], check=True)
            print(f"Backup creado: {backup_file}")

        # Generar el contenido del archivo
        lineas = []
        lineas.append("# /etc/exports")
        lineas.append("# Generado por NFS Configuration Tool")
        lineas.append(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("")

        for directorio, hosts in exports_data.items():
            if not hosts:
                continue  # No exportar directorios sin hosts

            linea = directorio
            for host, opciones in hosts:
                linea += f" {host}({opciones})"

            lineas.append(linea)

        # Escribir el archivo
        contenido = "\n".join(lineas) + "\n"

        with open(archivo, 'w') as f:
            f.write(contenido)

        print(f"Archivo {archivo} actualizado correctamente.")
        return True

    except PermissionError:
        raise PermissionError("No se puede escribir en /etc/exports. Ejecuta como root (sudo).")
    except Exception as e:
        raise Exception(f"Error al escribir {archivo}: {e}")


def recargar_exportfs():
    """
    Ejecuta 'exportfs -ra' para aplicar los cambios en el servidor NFS.
    """
    try:
        resultado = subprocess.run(
            ["exportfs", "-ra"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Servidor NFS recargado con éxito (exportfs -ra)")
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al ejecutar 'exportfs -ra': {e.stderr}")
    except FileNotFoundError:
        raise Exception("Comando 'exportfs' no encontrado. ¿Está instalado nfs-kernel-server?")
    except Exception as e:
        raise Exception(f"Error inesperado al recargar NFS: {e}")


def verificar_permisos():
    """
    Verifica si el usuario tiene permisos para modificar /etc/exports.
    """
    return os.access(EXPORTS_FILE, os.W_OK) or os.geteuid() == 0
