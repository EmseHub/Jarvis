(() => {
    const localStorageToImport = arguments[0];
    window.localStorage.clear();
    for (const key in localStorageToImport) {
        if (Object.hasOwnProperty.call(localStorageToImport, key)) {
            const element = localStorageToImport[key];
            window.localStorage.setItem(key, element);
        }
    }
})();