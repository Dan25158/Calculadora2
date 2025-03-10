
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

            # Formatear el resultado como HTML para mostrar detalles
            result = f"""
            <h3>Desglose de Costos:</h3>
            <p>Precio Inicial: ${precio_inicial:.2f} USD</p>
            
            {'<p>Tax 7%: $'+str(tax7)+'</p>' if form_data["aplicar_tax7"] else ''}
            
            <p>Envío USA a Paquetería: ${envio_usa:.2f} USD</p>
            <p>Base para impuestos: ${base_impuesto:.2f} USD</p>
            
            {'<p>Impuesto 24% (base > $200): $'+f"{additional_tax:.2f}"+' USD</p>' if base_impuesto > 200 else ''}
            
            <p>Envío a Perú (Peso: {peso:.2f} kg): ${envio_peru_base:.2f} USD</p>
            <hr>
            <p>Subtotal (antes de IGV): ${subtotal:.2f} USD</p>
            <p>IGV (18%): ${subtotal * 0.18:.2f} USD</p>
            <p><strong>Precio Final: ${final_price:.2f} USD</strong></p>
            """

        except ValueError:
            flash("Por favor, ingresa valores numéricos válidos para todos los campos.")

    return render_template("index.html", form_data=form_data, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
