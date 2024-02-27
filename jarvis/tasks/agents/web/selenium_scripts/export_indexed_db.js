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

                // console.log(value);
                // const iOa = value instanceof ArrayBuffer;
                // console.log("value instanceof ArrayBuffer", iOa);
                // const typeOf = typeof value;
                // console.log("typeof value", typeOf);

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
        // console.log(`IndexedDB "${name}" erfolgreich geladen.`, db);
        callback(openedDb);
    };
};


const getIndexedDbExport = (dbs, callback) => {

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



const normalizeValuesForExport = (obj) => {
    const checkIfValueIsArrayBuffer = (value) => (value && typeof value === "object" && value instanceof ArrayBuffer && value.byteLength !== undefined);
    const checkIfValueIsDate = (value) => (value && value instanceof Date && !isNaN(value));

    const stack = [obj];
    while (stack?.length > 0) {
        const currentObj = stack.pop();
        Object.keys(currentObj).forEach(key => {
            const value = currentObj[key];
            if (checkIfValueIsArrayBuffer(value)) {
                currentObj[key] = { "_isArrayBuffer_": true, "_Uint8Array_": Array.from(new Uint8Array(value)) };
            }
            else if (checkIfValueIsDate(value)) {
                currentObj[key] = { "_isDate_": true, "_ISOString_": value.toISOString() };
            }
            else if (typeof currentObj[key] === "object" && currentObj[key] !== null) {
                // Only iterate through nested value if it hasn't been changed and has a value  
                stack.push(currentObj[key]);
            }
        });
    }
};


window.indexedDB.databases().then((dbs) => {

    // const pushDbsToResultLoop = (result, dbs, callback) => {
    //     if (dbs.length === 0) {
    //         callback(result);
    //     }
    //     else {
    //         const curDb = dbs.shift();
    //         const curDbName = curDb.name;
    //         const curDbVersion = curDb.version;

    //         getOpenDb(curDbName, (callbackDb) => {
    //             if (callbackDb !== null) {

    //                 getAllObjectStores(callbackDb, (callbackDbObjectStores) => {
    //                     result.push({
    //                         "dbName": curDbName,
    //                         "dbVersion": curDbVersion,
    //                         "dbObjectStores": callbackDbObjectStores
    //                     });
    //                 });
    //             }
    //             pushDbsToResultLoop(result, dbs, callback);
    //         });
    //     }
    // };

    // pushDbsToResultLoop([], dbs, (cbResult) => {


    getIndexedDbExport(dbs, (cbIndexedDbExport) => {

        normalizeValuesForExport(cbIndexedDbExport);

        console.log("IndexedDB vollständig exportiert.");
        console.log(cbIndexedDbExport);
        selenium_callback(cbIndexedDbExport);
    });
})