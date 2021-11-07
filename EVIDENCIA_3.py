from collections import namedtuple
import time
import sys
import sqlite3
from sqlite3 import Error
#Evidencia 3

separador = "*" * 80
ventas = {} #Creando el diccionario donde se guardarán las ventas extraidas de la base de datos
Detalle_venta = namedtuple("Detalle_venta", "descripcion cantidad precio")
Clave_venta = namedtuple("Clave_venta", "folio fecha")

try:
    with sqlite3.connect("RegistroVentas.db") as conn: #Estableciendo conexión con la Base de datos. En caso de no existir, se procede a crearla junto con sus tablas.
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS claves_ventas (folio_venta INTEGER PRIMARY KEY, fecha_venta TEXT NOT NULL);")
        cursor.execute("CREATE TABLE IF NOT EXISTS detalles_ventas (folio_venta INTEGER, descripcion TEXT NOT NULL, cantidad INTEGER NOT NULL, precio REAL NOT NULL, FOREIGN KEY(folio_venta) REFERENCES claves_ventas(folio_venta));")
except Error as e:
    print(e)
except Exception:
    print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")
else: 
    print("Conexión establecida")
    
time.sleep(1)
while True:
    print(f"\n{separador}")
    print(f"{' VENTA DE COSMETICOS '.center(80,'=')}\n")
    print(f"{' Menú principal '.center(79,'=')}\n")
    print("1. Registrar una venta.\n")
    print("2. Consultar una venta.\n")
    print("3. Obtener un reporte de ventas para una fecha específica.\n")
    print("4. Salir\n")
    
    print(separador)
    respuesta = int(input("Escribe el número con la opción que deseas realizar: \n"))
    print(separador)
    
    if respuesta == 1:
        folio = int(input("Ingrese el folio: "))
        while True:
            try:
                with sqlite3.connect("RegistroVentas.db") as conn: #Accedemos a la base de datos para validar que la el folio ingresado no exista.
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT folio_venta FROM claves_ventas WHERE folio_venta = {folio}")
                    folio_existente = cursor.fetchall()
                    if folio_existente:
                        print("\nEste folio ya esta registrado, porfavor ingresa otro\n")
                        time.sleep(1)
                        break
                    else:
                        fecha = input("Ingresa la fecha de la venta (YYYY-MM-DD): ")
                        clave_venta = Clave_venta(folio, fecha)
                        articulos = []
                        
                    while True:
                        print(separador)
                        descripcion = input("\nDescipcion del articulo: ")
                        cantidad = int(input("Cantidad de piezas vendidas: "))
                        precio = float(input("Precio del articulo: "))
                            
                        articulo_en_turno = Detalle_venta(descripcion, cantidad, precio) #Reunir los detalles del articulo en una tupla nominada
                        articulos.append(articulo_en_turno) #Agregar los articulos de la venta a una lista 
                        
                        print(separador)
                        seguir_registrando = int(input("¿Seguir registrando ventas? Si=1, No=0: "))
                        
                        if seguir_registrando == 0: # Con los datos ingresados previamente, se registran en su respectiva tabla
                            gran_total = 0 
                            cursor.execute(f"INSERT INTO claves_ventas VALUES(?,?)", (clave_venta.folio, clave_venta.fecha)) # Registro de Claves en la tabla

                            for articulo in articulos:
                                total_articulo = articulo.cantidad * articulo.precio
                                gran_total = gran_total + total_articulo    # Registro de detalles de venta en la tabla
                                cursor.execute(f"INSERT INTO detalles_ventas VALUES(?,?,?,?)", (clave_venta.folio, articulo.descripcion, articulo.cantidad, articulo.precio))
                    
                            iva = gran_total * .16
                            total_mas_iva = gran_total + iva
                            print(separador)
                            print(f"El IVA (16%) de esta compra es de: ${iva:,.2f}")
                            print(f"\nEl total a pagar es de: ${total_mas_iva:,.2f}")
                            input("\nPresione ENTER para continuar...")
                            break
            except Error as e:
                print(e)
            except Exception:
                print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")
            finally:
                if conn:
                    conn.close()
                    break

    elif respuesta == 2:
        folio_busqueda = int(input("Ingresa el folio a consultar: ")) 
        try:
            with sqlite3.connect("RegistroVentas.db") as conn: #Creamos nueva conexión con base de datos 
                cursor = conn.cursor()
                folio_consulta = {'folio': folio_busqueda}
                cursor.execute(f"SELECT folio_venta FROM claves_ventas WHERE folio_venta = :folio", folio_consulta) # Validamos que el folio ingresado exista en la tabla 
                resultado_buscar_folio = cursor.fetchall()
                if resultado_buscar_folio: 
                    cursor.execute(f"""
                                    SELECT claves_ventas.folio_venta, claves_ventas.fecha_venta, \
                                    detalles_ventas.descripcion, detalles_ventas.cantidad, detalles_ventas.precio \
                                    FROM claves_ventas \
                                    INNER JOIN detalles_ventas \
                                    ON claves_ventas.folio_venta = detalles_ventas.folio_venta\
                                    WHERE claves_ventas.folio_venta = :folio """,folio_consulta)
                    registros = cursor.fetchall() # En caso de encontrarlo, consultar sus detalles de venta
                    clave =[] 
                    detalle_venta = []
                    for folio, fecha, descripcion, cantidad, precio in registros: # Se procede a juntar los articulos con su respectiva clave para poder imprimirlos
                        clave_venta = Clave_venta(folio, fecha)
                        if clave_venta not in clave:
                            clave.append(clave_venta)
                        articulo_en_turno = Detalle_venta(descripcion, cantidad, precio)
                        detalle_venta.append(articulo_en_turno)
                        
                    for elemento in clave:
                        print(f"El Folio de la venta es: {elemento.folio}") #Imprimir la venta con ese folio
                        print(f"La Fecha de la venta es: {elemento.fecha}")
                    print(f'\n{"Cantidad":<5} | {"Descripcion":<17} | {"Precio venta":<16} | {"Total":<20} \n')
                    total = 0
                    for articulo in detalle_venta:
                        print(f"{articulo.cantidad:<8} | {articulo.descripcion:<17} | ${articulo.precio:<15,.2f} | ${(articulo.cantidad) * (articulo.precio):,.2f}")
                        total_por_articulo = articulo.cantidad * articulo.precio
                        total = total + total_por_articulo
                    iva = total * .16
                    total_mas_iva = total + iva
                    print('_' * 60)
                    print(f"IVA (16%): ${iva:,.2f}")
                    print(f'Total de la venta: ${total_mas_iva:,.2f}')
                    input("\nPresione ENTER para continuar...")
                else:
                    print("\n-- No se encontro ninguna venta con el folio ingresado --") # Si no existe el folio, mostrar este mensaje
                    time.sleep(1)

        except Exception:
            print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")

    elif respuesta == 3:
        fecha_busqueda = input("Ingresa la fecha a consultar(YYYY-MM-DD): ")
        try:
            with sqlite3.connect("RegistroVentas.db") as conn: #Creamos nueva conexión con base de datos 
                cursor = conn.cursor()
                fecha_consulta = {'fecha': fecha_busqueda }
                cursor.execute("SELECT * FROM claves_ventas WHERE fecha_venta = :fecha", fecha_consulta) # Validamos que la fecha ingresada exista en la tabla 
                claves_ventas = cursor.fetchall() 
                
                if claves_ventas:
                    cursor.execute(f"""
                                    SELECT claves_ventas.folio_venta, claves_ventas.fecha_venta, \
                                    detalles_ventas.descripcion, detalles_ventas.cantidad, detalles_ventas.precio \
                                    FROM claves_ventas \
                                    INNER JOIN detalles_ventas \
                                    ON claves_ventas.folio_venta = detalles_ventas.folio_venta\
                                    WHERE claves_ventas.fecha_venta = :fecha """, fecha_consulta)
                    
                    ventas_por_fecha = cursor.fetchall()  # En caso de encontrarlo, consultar todas las ventas con esa fecha
                    print(separador)
                    for clave_folio, clave_fecha in claves_ventas: 
                        articulos = []
                        for detalle_folio, detalle_fecha, descripcion, cantidad, precio in ventas_por_fecha:  # Los detalles son relacionan con su respectiva clave
                            if clave_folio == detalle_folio:
                                total = 0
                                articulo_en_turno = Detalle_venta(descripcion, cantidad, precio)
                                articulos.append(articulo_en_turno)
                        print(f"\nEl Folio de la venta es: {clave_folio}") #Imprimir la venta con ese folio
                        print(f"La Fecha de la venta es: {clave_fecha}")
                        print(f'\n{"Cantidad":<5} | {"Descripcion":<17} | {"Precio venta":<16} | {"Total":<20} \n')
                        for articulo in articulos:
                            print(f"{articulo.cantidad:<8} | {articulo.descripcion:<17} | ${articulo.precio:<15,.2f} | ${(articulo.cantidad) * (articulo.precio):,.2f}")
                            total_por_articulo = articulo.cantidad * articulo.precio
                            total = total + total_por_articulo
                        iva = total * .16
                        total_mas_iva = total + iva
                        print('_' * 60)
                        print(f"IVA (16%): ${iva:,.2f}")
                        print(f'Total de la venta: ${total_mas_iva:,.2f}\n')
                        print(separador)
                    else:
                        input("\nPresione ENTER para continuar...")     
                else:
                    print("\n-- No se encontro ninguna venta con la fecha ingresada --") # En caso de no tener ventas con esa fecha
                    time.sleep(1)
        except Exception:
            print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")

    elif respuesta == 4:
        confirmacion = int(input("¿Esta seguro de que desea salir? (1=SI, 0=NO)")) # Salida del Programa
        if confirmacion == 1:
            break
    else:
        print("OPCION NO VALIDA")