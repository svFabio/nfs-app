
import os
import re
import subprocess
from datetime import datetime


EXPORTS_FILE = "/etc/exports"
EXPORTS_BACKUP = "/etc/exports.backup"


def parsear_exports(archivo=EXPORTS_FILE):

    if not os.path.exists(archivo):
        return {}

    exports_data = {}

    try:
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()


                if not linea or linea.startswith('#'):
                    continue

                partes = linea.split()
                if len(partes) < 2:
                    continue

                directorio = partes[0]
                hosts = []

                for host_opts in partes[1:]:

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

    try:

        if hacer_backup and os.path.exists(archivo):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{archivo}.backup.{timestamp}"
            subprocess.run(["cp", archivo, backup_file], check=True)
            print(f"Backup creado: {backup_file}")


        lineas = []
        lineas.append("# /etc/exports")
        lineas.append("# Generado por NFS Configuration Tool")
        lineas.append(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("")

        for directorio, hosts in exports_data.items():
            if not hosts:
                continue

            linea = directorio
            for host, opciones in hosts:
                linea += f" {host}({opciones})"

            lineas.append(linea)


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

    return os.access(EXPORTS_FILE, os.W_OK) or os.geteuid() == 0
