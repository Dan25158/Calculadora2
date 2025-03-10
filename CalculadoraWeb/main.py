import math
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"

@app.route("/", methods=["GET", "POST"])
def index():
    # Datos iniciales del formulario
    form_data = {
        "precio_inicial": "",
        "envio_usa": "",       # Envío USA a Paquetería (USD)
        "peso_paquete": "",
        "aplicar_tax7": False  # Checkbox para aplicar Tax del 7%
    }
    result = None

    if request.method == "POST":
        # Recoger y limpiar datos del formulario
        form_data["precio_inicial"] = request.form.get("precio_inicial", "").strip()
        form_data["envio_usa"] = request.form.get("envio_usa", "").strip()
        form_data["peso_paquete"] = request.form.get("peso_paquete", "").strip()
        form_data["aplicar_tax7"] = True if request.form.get("aplicar_tax7") == "on" else False

        try:
            # Convertir entradas a float
            precio_inicial = float(form_data["precio_inicial"])
            envio_usa = float(form_data["envio_usa"])
            peso = float(form_data["peso_paquete"])

            # Validar que el peso mínimo sea 0.1 kg
            if peso < 0.1:
                flash("El peso debe ser al menos 0.1 kg.")
                return render_template("index.html", form_data=form_data, result=result)

            # 1. Tax opcional del 7%
            tax7 = precio_inicial * 0.07 if form_data["aplicar_tax7"] else 0

            # 2. Calcular la base para impuestos:
            # Base = Precio Inicial + Tax 7% (si se aplica) + Envío USA a Paquetería
            base_impuesto = precio_inicial + tax7 + envio_usa

            # 3. Impuesto del 24% se aplica solo si la base supera 200 USD
            additional_tax = base_impuesto * 0.24 if base_impuesto > 200 else 0

            # 4. Determinar el costo de Envío a Perú según el peso:
            if peso >= 0.1 and peso <= 0.5:
                envio_peru_base = 15.34
            elif peso <= 1.0:
                envio_peru_base = 22.42
            elif peso <= 1.5:
                envio_peru_base = 28.32
            elif peso <= 2.0:
                envio_peru_base = 33.04
            else:
                # Para peso mayor a 2.0 kg, cada 0.5 kg adicional aumenta el costo en el promedio de las diferencias
                # Calculamos el promedio de incremento de los rangos dados:
                # Diferencias: 22.42-15.34=7.08, 28.32-22.42=5.90, 33.04-28.32=4.72 → Promedio ≈ (7.08+5.90+4.72)/3 = 5.90
                extra_units = math.ceil((peso - 2.0) / 0.5)
                envio_peru_base = 33.04 + extra_units * 5.90

            # 5. Sumar todos los elementos (antes del IGV):
            subtotal = base_impuesto + additional_tax + envio_peru_base

            # 6. Aplicar IGV del 18%
            final_price = subtotal * 1.18

            # Preparar el desglose en HTML
            result = f"""
            <h2>Resumen del Cálculo</h2>
            <strong>Precio Inicial:</strong> ${precio_inicial:.2f}<br>
            <strong>Tax 7% (opcional):</strong> ${tax7:.2f}<br>
            <strong>Envío USA a Paquetería:</strong> ${envio_usa:.2f}<br>
            <hr>
            <strong>Base para impuestos:</strong> ${base_impuesto:.2f}<br>
            <strong>Impuesto 24% (si base >200 USD):</strong> ${additional_tax:.2f}<br>
            <hr>
            <strong>Envío a Perú (según peso {peso:.2f} kg):</strong> ${envio_peru_base:.2f}<br>
            <hr>
            <strong>Subtotal (sin IGV):</strong> ${subtotal:.2f}<br>
            <strong>IGV (18%):</strong> ${(subtotal * 0.18):.2f}<br>
            <hr>
            <h3>COSTO FINAL EN USD: ${final_price:.2f}</h3>
            """

        except ValueError:
            flash("Por favor, ingresa valores numéricos válidos en todos los campos.")

    return render_template("index.html", form_data=form_data, result=result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
