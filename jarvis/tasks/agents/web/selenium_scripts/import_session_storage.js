const sessionStorageToImport = arguments[0];
window.sessionStorage.clear();
for (const key in sessionStorageToImport) {
    if (Object.hasOwnProperty.call(sessionStorageToImport, key)) {
        const element = sessionStorageToImport[key];
        window.sessionStorage.setItem(key, element);
    }
}