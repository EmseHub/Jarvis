const indexedDbToImport = arguments[0];
const selenium_callback = arguments[arguments.length - 1];


const putItemsIntoDb = (openedDb, objectStoreToImport, callbackPut) => {

    const transaction = openedDb.transaction([objectStoreToImport.name], "readwrite");

    transaction.oncomplete = (event) => {
        // console.log(`Alle Items von "${objectStoreName.name}" erfolgreich hinzugefügt.`);
        callbackPut(true);
    };
    transaction.onerror = (event, source, lineno, colno, error) => {
        console.warn(`Error beim hinzufügen der Items von "${objectStoreToImport.name}"`);
        console.warn(event);
        callbackPut(false);
    };

    const objectStore = transaction.objectStore(objectStoreToImport.name);
    const keyPath = objectStoreToImport["keyPath"];

    for (const item of objectStoreToImport["items"]) {

        const primaryKey = item["primaryKey"];
        const value = item["value"];

        // Wenn Object Store In-Line Keys verwendet ( = keyPath vorhanden), darf bei put kein Key-Argument übergeben werden
        const putRequest = ((keyPath === null || keyPath === undefined) && (primaryKey !== null && primaryKey !== undefined))
            ? objectStore.put(value, primaryKey)
            : objectStore.put(value);

        putRequest.onsuccess = (event) => {
            // console.log("Item hinzugefügt.", putRequest.result);
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

        const sample_export = [
            {
                "dbName": "cars",
                "dbVersion": 2,
                "dbObjectStores": [
                    {
                        "name": "some_table_name",
                        "keyPath": "sth",
                        // "primaryKeyPath": "some_id_or_key",
                        "autoIncrement": false,
                        "indices": [
                            {
                                "name": "index_name",
                                "keyPath": "sth",
                                "options": {
                                    "unique": false,
                                    "multiEntry": false
                                }
                            },
                        ],
                        "items": [
                            {
                                "primaryKey": 66,
                                "value": {
                                    "some_id_or_key": 66,
                                    "sth": {
                                        "algorithm": {
                                            "name": "HKDF"
                                        },
                                        "extractable": false,
                                        "type": "secret",
                                        "usages": [
                                            "deriveKey"
                                        ]
                                    }
                                }
                            },
                        ]
                    },
                ]
            },
        ];

        // Create object stores in DB (an object store corresponds to a table)
        for (const objectStoreToImport of dbObjectStores) {

            const name = objectStoreToImport["name"];
            const keyPath = objectStoreToImport["keyPath"];
            const autoIncrement = objectStoreToImport["autoIncrement"];

            // keyPath entspricht dem, was in anderen DB der Primary Key ist
            // autoIncrement immer auf false, um eigenen Wert zuzuweisen
            const options = { autoIncrement: autoIncrement };
            if (keyPath !== null && keyPath !== undefined) { options.keyPath = keyPath; }

            const store = upgradingDb.createObjectStore(name, options);

            for (const index of objectStoreToImport["indices"]) {
                store.createIndex(index["name"], index["keyPath"], index["options"]);
            }
        }
    }

    DBOpenRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${dbName}" erfolgreich erstellt.`);

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


const denormalizeValuesForImport = (obj) => {
    const checkIfValueWasArrayBuffer = (value) => value && typeof value === "object" && value.constructor === Object && value.hasOwnProperty("_isArrayBuffer_");
    const checkIfValueWasDate = (value) => (value && typeof value === "object" && value.constructor === Object && value.hasOwnProperty("_isDate_"));

    const stack = [obj];
    while (stack?.length > 0) {
        const currentObj = stack.pop();
        Object.keys(currentObj).forEach(key => {
            const value = currentObj[key];
            if (checkIfValueWasArrayBuffer(value)) {
                const uint8Array = Uint8Array.from(value["_Uint8Array_"]);
                currentObj[key] = uint8Array.buffer;
            }
            else if (checkIfValueWasDate(value)) {
                currentObj[key] = new Date(value["_ISOString_"]);
            }
            else if (typeof currentObj[key] === "object" && currentObj[key] !== null) {
                // Only iterate through nested value if it hasn't been changed and has a value  
                stack.push(currentObj[key]);
            }
        });
    }
};


if (!indexedDbToImport || indexedDbToImport.length === 0) {
    selenium_callback(true);
}
else {
    denormalizeValuesForImport(indexedDbToImport);
    let importedDbsCount = 0;
    for (const db of indexedDbToImport) {
        createDb(db, (cbIsCreated) => {
            importedDbsCount++;
            if (importedDbsCount === indexedDbToImport.length) {
                console.log("Alle Einträge der IndexedDB eingelesen.");
                selenium_callback(true);
            }
        });
    }
}