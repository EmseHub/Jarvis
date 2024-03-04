(() => {
    const indexedDbToImport = arguments[0];
    const selenium_callback = arguments[arguments.length - 1];


    const putItemsIntoDb = (openedDb, objectStoreToImport, callbackPut) => {

        const transaction = openedDb.transaction([objectStoreToImport.name], "readwrite");

        transaction.oncomplete = (event) => {
            // console.log(`All items of "${objectStoreName.name}" successfully added.`);
            callbackPut(true);
        };
        transaction.onerror = (event, source, lineno, colno, error) => {
            console.warn(`Error when adding items to "${objectStoreToImport.name}"`);
            console.warn(event);
            callbackPut(false);
        };

        const objectStore = transaction.objectStore(objectStoreToImport.name);
        const keyPath = objectStoreToImport["keyPath"];

        for (const item of objectStoreToImport["items"]) {

            const primaryKey = item["primaryKey"];
            const value = item["value"];

            // If object store uses in-line keys ( = keyPath exists), don't use put() with key argument
            const putRequest = ((keyPath === null || keyPath === undefined) && (primaryKey !== null && primaryKey !== undefined))
                ? objectStore.put(value, primaryKey)
                : objectStore.put(value);

            putRequest.onsuccess = (event) => {
                // console.log("Item added.", putRequest.result);
                // console.log(newItem);
            };
            putRequest.onerror = (event) => {
                console.warn(`Error beim Hinzufügen (Put) eines Items: ${item}`);
                console.warn(event);
            }
        }
    };


    const createDb = ({ dbName, dbVersion, dbObjectStores }, callback) => {

        const DBOpenRequest = window.indexedDB.open(dbName, dbVersion);

        DBOpenRequest.onerror = (event) => {
            console.warn(`IndexedDB "${dbName}" konnte nicht erstellt werden.`);
            console.warn(error);
            callback(false);
        };

        // onupgradeneeded --> Triggered when a new DB is created or the version of an existing DB is changed
        DBOpenRequest.onupgradeneeded = (event) => {
            // Save new DB in constant
            const upgradingDb = DBOpenRequest.result;

            // Create object stores in DB (an object store corresponds to a table)
            for (const objectStoreToImport of dbObjectStores) {

                const name = objectStoreToImport["name"];
                const keyPath = objectStoreToImport["keyPath"];
                const autoIncrement = objectStoreToImport["autoIncrement"];

                // keyPath corresponds to what the primary key is in other database management systems
                const options = { autoIncrement: autoIncrement };
                if (keyPath !== null && keyPath !== undefined) { options.keyPath = keyPath; }

                const store = upgradingDb.createObjectStore(name, options);

                for (const index of objectStoreToImport["indices"]) {
                    store.createIndex(index["name"], index["keyPath"], index["options"]);
                }
            }
        }

        DBOpenRequest.onsuccess = (event) => {
            console.log(`IndexedDB "${dbName}" successfully created.`);

            const openedDb = DBOpenRequest.result;

            let populatedCount = 0;
            for (const objectStoreToImport of dbObjectStores) {
                putItemsIntoDb(openedDb, objectStoreToImport, (cbIsPut) => {
                    populatedCount++;
                    if (populatedCount === dbObjectStores.length) {
                        openedDb.close();
                        callback(cbIsPut);
                    }
                });
            }
        };
    };


    const denormalizeValuesForImport = (obj, callback) => {
        // Converts all exported serialized values back to their original form
        const checkIfValueWasCryptoKey = (value) => value && typeof value === "object" && value.constructor === Object && value.hasOwnProperty("_isCryptoKey_");
        const checkIfValueWasArrayBuffer = (value) => value && typeof value === "object" && value.constructor === Object && value.hasOwnProperty("_isArrayBuffer_");
        const checkIfValueWasDate = (value) => (value && typeof value === "object" && value.constructor === Object && value.hasOwnProperty("_isDate_"));

        const getCryptoKey = (customCryptoKeyObj, callbackCryptoKey) => {
            // Re-convert serializable object into CryptoKey
            if (!customCryptoKeyObj) { callbackCryptoKey(null); return; }
            // importKey(format, keyData, algorithm, extractable, keyUsages)
            console.log(customCryptoKeyObj);
            window.crypto.subtle.importKey(
                "jwk",
                customCryptoKeyObj["jwk"],
                customCryptoKeyObj["algorithm"],
                customCryptoKeyObj["extractable"],
                customCryptoKeyObj["usages"]
            ).then((cryptoKey) => { callbackCryptoKey(cryptoKey); });
        }

        const stack = [obj];
        let pendingActionsCount = 1;

        const interval = setInterval(function () {
            console.log("Denormalization of IndexedDB data in progress...");
            if (stack.length === 0 && pendingActionsCount === 0) {
                clearInterval(interval);
                callback(true);
            }
        }, 100);

        while (stack?.length > 0) {
            const currentObj = stack.pop();
            Object.keys(currentObj).forEach(curKey => {
                const value = currentObj[curKey];
                if (checkIfValueWasCryptoKey(value)) {
                    pendingActionsCount++;
                    getCryptoKey(value["_customCryptoKeyObj_"], (cbCryptoKey) => {
                        currentObj[curKey] = cbCryptoKey;
                        pendingActionsCount--;
                    });
                }
                else {
                    if (checkIfValueWasArrayBuffer(value)) {
                        const uint8Array = Uint8Array.from(value["_Uint8Array_"]);
                        currentObj[curKey] = uint8Array.buffer;
                    }
                    else if (checkIfValueWasDate(value)) {
                        currentObj[curKey] = new Date(value["_ISOString_"]);
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


    if (!indexedDbToImport || indexedDbToImport.length === 0) {
        selenium_callback(true);
    }
    else {
        denormalizeValuesForImport(indexedDbToImport, (cbIsDenormalized) => {
            let importedDbsCount = 0;
            for (const db of indexedDbToImport) {
                createDb(db, (cbIsCreated) => {
                    importedDbsCount++;
                    if (importedDbsCount === indexedDbToImport.length) {
                        console.log("All IndexedDB entries imported.");
                        selenium_callback(true);
                    }
                });
            }
        });
    }
})();