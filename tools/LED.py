from tools.kiwilog import kiwi
log = kiwi.instance('tools.LED')
try:
    from periphery import GPIO
    cur_col = ''
    log.add_log("Sucessfully imported periphery.GPIO")

    b = GPIO(77, "out") # Actually blue
    r = GPIO(73, "out") # Actually red
    g = GPIO(138, "out") # Actually green
    ir = GPIO(141, "out")

    def red():
        global cur_col
        if cur_col != 'red':
            log.add_log("LEDMode changed to RED")
            cur_col = 'red'

            r.write(True)
            g.write(False)
            b.write(False)

    def green():
        global cur_col
        if cur_col != 'green':
            log.add_log("LEDMode changed to GREEN")
            cur_col = 'green'
            r.write(False)
            g.write(True)
            b.write(False)

    def blue():
        global cur_col
        if cur_col != 'blue':
            log.add_log("LEDMode changed to BLUE")
            cur_col = 'blue'
            r.write(False)
            g.write(False)
            b.write(True)

    def off():
        global cur_col
        if cur_col != 'off':
            log.add_log("LEDMode changed to OFF")
            cur_col = 'off'
            r.write(False)
            g.write(False)
            b.write(False)

    def IRon():
        # I know it's backwards.
        ir.write(False)

    def IRoff():
        ir.write(True)
except Exception as e:
    log.add_exception(f"Error importing periphery library. Using dummy LED controls.  Exception: {e} ")
    def red():
        ...

    def green():
        ...


    def blue():
        ...


    def IRon():
        ...

    def IRoff():
        ...