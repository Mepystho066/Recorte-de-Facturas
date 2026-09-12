def fecha_actual():
    date_time = datetime.now()
    fecha_formateada = date_time.strftime("%d-%m-%Y")
    return fecha_formateada