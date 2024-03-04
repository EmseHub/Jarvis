(() => {
    const selenium_callback = arguments[arguments.length - 1];


    const getObjectStores = (openedDb, callback) => {
        const dbObjectStores = [];
        if (!openedDb || openedDb.objectStoreNames.length === 0) {
            callback(dbObjectStores);
            return;
        }

        const transaction = openedDb.transaction(openedDb.objectStoreNames, "readonly");
        for (const storeName of openedDb.objectStoreNames) {
            const allObjects = [];

            const objectStore = transaction.objectStore(storeName);
            const keyPath = objectStore.keyPath;
            const autoIncrement = objectStore.autoIncrement;

            const indices = [];
            const indexNames = objectStore.indexNames;
            for (let i = 0; i < indexNames.length; i++) {
                const index = objectStore.index(indexNames[i]);
                indices.push({
                    name: index.name,
                    keyPath: index.keyPath,
                    options: {
                        "unique": index.unique,
                        "multiEntry": index.multiEntry
                    }
                });
            }
            // console.log(`---${storeName}---`);
            objectStore.openCursor().onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    // Cursor holds value, put it into store data
                    const value = cursor.value;

                    allObjects.push({
                        "primaryKey": cursor.primaryKey,
                        "value": cursor.value
                    });

                    cursor.continue();
                } else {
                    // No more items, store is done
                    const dbStore = {
                        "name": storeName,
                        "keyPath": keyPath,
                        "autoIncrement": autoIncrement,
                        "indices": indices,
                        "items": allObjects
                    };
                    dbObjectStores.push(dbStore);

                    // Last store was handled
                    if (dbObjectStores.length === openedDb.objectStoreNames.length) {
                        callback(dbObjectStores);
                    }
                }
            };
        }
    };


    const getOpenedDb = (dbName, callback) => {
        const DBOpenRequest = window.indexedDB.open(dbName);
        DBOpenRequest.onerror = (event) => {
            console.warn(`IndexedDB "${dbName}" konnte nicht geladen werden.`, event);
            callback(null);
        };
        DBOpenRequest.onsuccess = (event) => {
            const openedDb = DBOpenRequest.result;
            // console.log(`IndexedDB "${name}" successfully loaded.`, db);
            callback(openedDb);
        };
    };


    const getIndexedDbExport = (dbs, callback) => {
        if (!dbs || dbs.length === 0) { callback([]); return; }

        const indexedDbExport = [];
        let processedDbsCount = 0;

        for (const db of dbs) {
            const dbName = db.name;
            const dbVersion = db.version;
            getOpenedDb(dbName, (cbOpenedDb) => {
                getObjectStores(cbOpenedDb, (cbDbObjectStores) => {
                    if (cbOpenedDb !== null) {
                        indexedDbExport.push({
                            "dbName": dbName,
                            "dbVersion": dbVersion,
                            "dbObjectStores": cbDbObjectStores
                        });
                    }
                    processedDbsCount++;
                    if (processedDbsCount === dbs.length) {
                        callback(indexedDbExport);
                    }
                });
            });
        }
    };


    const normalizeValuesForExport = (obj, callback) => {
        // Converts all IndexedDB values so that they can be serialized
        if (!obj) { callback(false); return; }
        const checkIfValueIsCryptoKey = (value) => (value && typeof value === "object" && value instanceof CryptoKey && value.toString() === "[object CryptoKey]");
        const checkIfValueIsArrayBuffer = (value) => (value && typeof value === "object" && value instanceof ArrayBuffer && value.byteLength !== undefined);
        const checkIfValueIsDate = (value) => (value && value instanceof Date && !isNaN(value));

        const getCustomCryptoKeyObj = (cryptoKey, callbackCustomCryptoKeyObj) => {
            // Convert CryptoKey into serializable object (if key is extractable)
            if (!cryptoKey?.extractable) { callbackCustomCryptoKeyObj(null); return; }
            window.crypto.subtle.exportKey("jwk", cryptoKey).then((jwk) => {
                const customCryptoKeyObj = {
                    "jwk": jwk,
                    "type": cryptoKey.type,
                    "algorithm": cryptoKey.algorithm,
                    "extractable": cryptoKey.extractable,
                    "usages": cryptoKey.usages
                };
                callbackCustomCryptoKeyObj(customCryptoKeyObj);
            });
        };

        const stack = [obj];
        let pendingActionsCount = 1;

        const interval = setInterval(function () {
            console.log("Normalization of IndexedDB data in progress...");
            if (stack.length === 0 && pendingActionsCount === 0) {
                clearInterval(interval);
                callback(true);
            }
        }, 100);

        // https://stackoverflow.com/questions/8085004/iterate-through-nested-javascript-objects
        while (stack?.length > 0) {
            const currentObj = stack.pop();
            Object.keys(currentObj).forEach(curKey => {
                const value = currentObj[curKey];
                if (checkIfValueIsCryptoKey(value)) {
                    pendingActionsCount++;
                    getCustomCryptoKeyObj(value, (cbCustomCryptoKeyObj) => {
                        currentObj[curKey] = { "_isCryptoKey_": true, "_customCryptoKeyObj_": cbCustomCryptoKeyObj };
                        pendingActionsCount--;
                    });
                }
                else {
                    if (checkIfValueIsArrayBuffer(value)) {
                        currentObj[curKey] = { "_isArrayBuffer_": true, "_Uint8Array_": Array.from(new Uint8Array(value)) };
                    }
                    else if (checkIfValueIsDate(value)) {
                        currentObj[curKey] = { "_isDate_": true, "_ISOString_": value.toISOString() };
                    }
                    else if (typeof currentObj[curKey] === "object" && currentObj[curKey] !== null) {
                        // Only iterate through nested value if it hasn't been changed and has a value  
                        stack.push(currentObj[curKey]);
                    }
                }
            });
        }
        pendingActionsCount--;
    };


    window.indexedDB.databases().then((dbs) => {
        getIndexedDbExport(dbs, (cbIndexedDbExport) => {
            if (!cbIndexedDbExport || cbIndexedDbExport.length === 0) { selenium_callback(null); return; }
            else {
                normalizeValuesForExport(cbIndexedDbExport, (cbIsNormalized) => {
                    console.log("All IndexedDB entries exported.");
                    console.log(cbIndexedDbExport);
                    selenium_callback(cbIndexedDbExport);
                });
            }
        });
    })
})();