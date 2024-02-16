const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSynth = window.speechSynthesis;
let arrVoices = speechSynth.getVoices();
speechSynth.onvoiceschanged = () => { arrVoices = speechSynth.getVoices(); };

let curSpeechRecognition;

export function recognizeTextFromSpeech(callback) {
    // console.time('Laufzeit recognizeTextFromSpeech');
    curSpeechRecognition = new SpeechRecognition();

    curSpeechRecognition.continuous = false; // Default false (Return continuous results for each recognition?)
    curSpeechRecognition.lang = 'de-DE';
    curSpeechRecognition.interimResults = false; // Interim results are results that are not yet final 
    curSpeechRecognition.maxAlternatives = 1; // Sets the maximum number of SpeechRecognitionAlternatives provided per result. The default value is 1.

    let isNoResult = true;

    curSpeechRecognition.onresult = (event) => {
        isNoResult = false;
        let transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');
        transcript = transcript.charAt(0).toUpperCase() + transcript.slice(1); // Ersten Buchstaben kapitalisieren
        transcript = transcript.replace(/(?<=\d)\s+(?=\d)/g, ''); // White-Space zwischen Zahlen entfernen
        callback(transcript);
    };

    curSpeechRecognition.onend = () => {
        if (isNoResult) {
            // console.timeEnd('Laufzeit recognizeTextFromSpeech');
            console.log('Speech-Recognition-Service ohne Ergebnis beendet');
            callback('');
        }
    };

    curSpeechRecognition.start();
}

export function speakUtteranceFromText(strText, callback) {
    if (!strText || !strText.trim()) {
        speechSynth.cancel();
        callback(false);
        return;
    }
    if (!arrVoices || arrVoices.length === 0) {
        console.log('Keine Voices');
        callback(false);
        return;
    }

    let voice = arrVoices.find(voice => voice.name === 'Google español');
    if (!voice) { voice = arrVoices.find(voice => voice.name === 'Google Deutsch'); }
    if (!voice) { voice = arrVoices.find(voice => voice.lang === 'de-DE'); }
    if (!voice) { voice = arrVoices[0]; }


    const speechSynthUtterance = new SpeechSynthesisUtterance();
    speechSynthUtterance.text = strText;
    speechSynthUtterance.voice = voice;
    speechSynthUtterance.lang = 'de-DE'; // Ohne Angaben wird <html> lang verwendet
    speechSynthUtterance.pitch = 1; // Default 1 (float zwischen 0 und 2)
    speechSynthUtterance.rate = 1.2; // Default 1 (float zwischen 0.1 und 10)
    speechSynthUtterance.volume = 1; // Default 1 (float zwischen 0 und 1)
    speechSynth.speak(speechSynthUtterance);

    speechSynthUtterance.onend = (event) => {
        // console.log(`Utterance ausgesprochen in ${(event.elapsedTime / 1000).toFixed(2)} Sekunden`);
        callback(true);
    };
    speechSynthUtterance.onerror = (event) => {
        if (event.error === 'interrupted') {
            callback(true);
            return;
        }
        console.log(`Fehler beim Aussprechen der Utterance: ${event.error}`);
        callback(false);
    };
}

export function stopTextFromSpeechRecognition() {
    if (curSpeechRecognition) {
        curSpeechRecognition.stop();
        curSpeechRecognition = null;
    }
}

export function cancelSpeechFromTextUtterances() {
    if (speechSynth) { speechSynth.cancel(); }
}