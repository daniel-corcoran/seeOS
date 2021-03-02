try:
    from periphery import PWM
    import time
    pwm = PWM(2, 0)
    pwm.frequency = 1e3
    pwm.duty_cycle = 0.5
    def enable_buzzer():
        pwm.enable()
    def disable_buzzer():
        pwm.disable()
    def set_freq(freq):
        pwm.frequency = freq
    def cooltone():
        enable_buzzer()
        for x in [587.330, 793.989, 880, 1174.66]:
            pwm.frequency = x
            time.sleep(0.161)
        disable_buzzer()
    def b_tone():
        enable_buzzer()
        for x in [1174.66, 880,  793.989, 587.330]:
            pwm.frequency = x
            time.sleep(0.161)
        disable_buzzer()
except:
    print("Could not import periphery lib.")
    def enable_buzzer():
        pass
    def disable_buzzer():
        pass
    def set_freq(freq):
        pass
    def cooltone():
        pass
    def b_tone():
        pass