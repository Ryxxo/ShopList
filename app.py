from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)

conexion = sqlite3.connect('shoplist.db', check_same_thread=False)

def crear_tabla():
    with sqlite3.connect('shoplist.db') as conexion:
        conexion.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                "Nombre del Producto" TEXT,
                "Cantidad del Producto" INTEGER,
                "Precio del Producto" INTEGER,
                "Comprado" TEXT
            )
        ''')
    print("Tabla 'productos' verificada o creada.")

def guardar_sql():
    if Lista:
        df = pd.DataFrame(Lista)
        with sqlite3.connect('shoplist.db') as conexion:
            conexion.execute('PRAGMA busy_timeout = 3000')
            df.to_sql('productos', con=conexion, if_exists='replace', index=False)
    else:
        with sqlite3.connect('shoplist.db') as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos")
            conexion.commit()

def cargar_sql():
    df = pd.read_sql('SELECT * FROM productos', con=conexion)
    global Lista
    Lista = df.to_dict(orient='records')

crear_tabla()

cargar_sql()

@app.route('/')
def index():
    return render_template('index.html', productos=Lista)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = int(request.form['precio'])
    comprado = "No"

    nuevo_producto = {
        "Nombre del Producto": nombre,
        "Cantidad del Producto": cantidad,
        "Precio del Producto": precio,
        "Comprado": comprado
    }
    
    Lista.append(nuevo_producto)
    guardar_sql()
    return redirect(url_for('index'))

@app.route('/eliminar/<nombre>', methods=['POST'])
def eliminar(nombre):
    global Lista
    Lista = [producto for producto in Lista if producto["Nombre del Producto"] != nombre]
    guardar_sql()
    return redirect(url_for('index'))

@app.route('/marcar/<nombre>', methods=['POST'])
def marcar(nombre):
    for producto in Lista:
        if producto["Nombre del Producto"] == nombre:
            producto["Comprado"] = "Si"
            break
    guardar_sql()
    return redirect(url_for('index'))

@app.route('/desmarcar/<nombre>', methods=['POST'])
def desmarcar(nombre):
    for producto in Lista:
        if producto["Nombre del Producto"] == nombre:
            producto["Comprado"] = "No"
            break
    guardar_sql()
    return redirect(url_for('index'))

@app.route('/actualizar/<nombre>', methods=['POST'])
def actualizar(nombre):
    nueva_cantidad = request.form['cantidad']
    nuevo_precio = request.form['precio']
    
    for producto in Lista:
        if producto["Nombre del Producto"] == nombre:
            if nueva_cantidad:
                producto["Cantidad del Producto"] = int(nueva_cantidad)
            if nuevo_precio:
                producto["Precio del Producto"] = int(nuevo_precio)
            break
    guardar_sql()
    return redirect(url_for('index'))

@app.route('/borrar_lista', methods=['POST'])
def borrar_lista():
    global Lista
    Lista.clear()
    
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos")
    conexion.commit()
    
    guardar_sql()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
