import os


def shutdown_computer():
    os_name = os.name

    if os_name == "nt":
        # Windows
        seconds_till_shutdown = 60
        shutdown_comment = "Heruntergefahren durch J.A.R.V.I.S."
        os.system(f'shutdown /s /t {seconds_till_shutdown} /c "{shutdown_comment}"')
        return {
            "feedback_text": f"Gerät wird in {seconds_till_shutdown} Sekunden heruntergefahren...",
            "is_successful": True,
        }
    elif os_name == "posix":
        # Unix/Linux/Mac
        # TODO: TESTEN
        minutes_till_shutdown = 1
        os.system(f'sudo shutdown -h +{minutes_till_shutdown}')
        return {"feedback_text": f"Gerät wird in {minutes_till_shutdown} {"Minute" if minutes_till_shutdown == 1 else "Minuten"} heruntergefahren...", "is_successful": True}
    else:
        return {
            "feedback_text": "Herunterfahren des Systems nicht möglich, da Betriebssystem unbekannt.",
            "is_successful": False,
        }


def hibernate_computer():
    os_name = os.name

    if os_name == "nt":
        # Windows
        seconds_till_hibernation = 20
        os.system(f'timeout /t {seconds_till_hibernation} /NOBREAK > NUL && shutdown /h')
        return {
            "feedback_text": f"Gerät wird in {seconds_till_hibernation} Sekunden in den Ruhezustand versetzt...",
            "is_successful": True,
        }
    elif os_name == "posix":
        # Unix/Linux/Mac
        # TODO: TESTEN
        minutes_till_sleep = 1
        os.system(f'sudo shutdown -s +{minutes_till_sleep}')
        return {"feedback_text": f"Gerät wird in {minutes_till_sleep} {"Minute" if minutes_till_sleep == 1 else "Minuten"} in den Ruhezustand versetzt...", "is_successful": True}
    else:
        return {
            "feedback_text": "Systems kann nicht in den Ruhezustand versetzt werden, da Betriebssystem unbekannt.",
            "is_successful": False,
        }


# System zustand specichern und Programm beenden vor shutdown
