import os


def hibernate_computer():
    feedback_text = None
    is_successful = False
    os_name = os.name

    if os_name == "nt":
        # Windows
        seconds_till_hibernation = 30
        try:
            os.startfile(
                filepath="cmd",
                arguments=f"/c timeout /t {seconds_till_hibernation} /NOBREAK > NUL && rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            )
            feedback_text = f"Gerät wird in {seconds_till_hibernation} Sekunden in den Energiesparmodus versetzt..."
            is_successful = True
        except Exception as e:
            print("Fehler beim Versetzen in den Energiesparmodus:", e)
            # Nur möglich, wenn in Win-Einstellungen Ruhezustand aktiviert wurde
            os.system(f"timeout /t {seconds_till_hibernation} /NOBREAK > NUL && shutdown /h")
            feedback_text = f"Gerät wird in {seconds_till_hibernation} Sekunden in den Ruhezustand versetzt..."
            is_successful = True
    elif os_name == "posix":
        # Unix/Linux/Mac
        # TODO: TESTEN
        minutes_till_sleep = 1
        os.system(f"sudo shutdown -s +{minutes_till_sleep}")
        feedback_text = f"Gerät wird in {minutes_till_sleep} {'Minute' if minutes_till_sleep == 1 else 'Minuten'} in den Ruhezustand versetzt..."
        is_successful = True
    else:
        feedback_text = "Systems kann nicht in den Ruhezustand versetzt werden, da Betriebssystem unbekannt."
        is_successful = False

    return (feedback_text, is_successful)


def shutdown_computer():
    feedback_text = None
    is_successful = False
    os_name = os.name

    if os_name == "nt":
        # Windows
        seconds_till_shutdown = 60
        shutdown_comment = "In knapp 60 Sekunden wird J.A.R.V.I.S. das System herunterfahren."
        os.system(f'shutdown /s /t {seconds_till_shutdown} /c "{shutdown_comment}"')
        feedback_text = f"Gerät wird in {seconds_till_shutdown} Sekunden heruntergefahren..."
        is_successful = True
    elif os_name == "posix":
        # Unix/Linux/Mac
        # TODO: TESTEN
        minutes_till_shutdown = 1
        os.system(f"sudo shutdown -h +{minutes_till_shutdown}")
        feedback_text = f"Gerät wird in {minutes_till_shutdown} {'Minute' if minutes_till_shutdown == 1 else 'Minuten'} heruntergefahren..."
        is_successful = True
    else:
        feedback_text = "Herunterfahren des Systems nicht möglich, da Betriebssystem unbekannt."
        is_successful = False

    return (feedback_text, is_successful)


def restart_computer():
    feedback_text = None
    is_successful = False
    os_name = os.name

    if os_name == "nt":
        # Windows
        seconds_till_restart = 60
        shutdown_comment = "In knapp 60 Sekunden wird J.A.R.V.I.S. das System neu starten."
        os.system(f'shutdown /r /t {seconds_till_restart} /c "{shutdown_comment}"')
        feedback_text = f"Gerät wird in {seconds_till_restart} Sekunden neu gestartet..."
        is_successful = True
    elif os_name == "posix":
        # Unix/Linux/Mac
        # TODO: TESTEN
        minutes_till_restart = 1
        os.system(f"sudo shutdown -r +{minutes_till_restart}")
        feedback_text = f"Gerät wird in {minutes_till_restart} {'Minute' if minutes_till_restart == 1 else 'Minuten'} neu gestartet..."
        is_successful = True
    else:
        feedback_text = "Neustart des Systems nicht möglich, da Betriebssystem unbekannt."
        is_successful = False

    return (feedback_text, is_successful)


# TODO Systemzustand speichern und Programm beenden vor Shutdown/Neustart
