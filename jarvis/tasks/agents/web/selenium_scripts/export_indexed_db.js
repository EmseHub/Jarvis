const selenium_callback = arguments[arguments.length - 1];

const openDb = (name, callback) => {
    const DBOpenRequest = window.indexedDB.open(name);
    DBOpenRequest.onerror = (event) => {
        console.warn(`IndexedDB "${name}" konnte nicht geladen werden.`, event);
        callback(null);
    };

    DBOpenRequest.onsuccess = (event) => {
        const db = DBOpenRequest.result;
        // console.log(`IndexedDB "${name}" erfolgreich geladen.`, db);
        callback(db);
    };
};

const getAllObjectStores = (db, callback) => {
    const dbStores = [];
    if (db.objectStoreNames.length === 0) {
        callback(dbStores);
    }
    else {
        const transaction = db.transaction(db.objectStoreNames, 'readonly');
        for (const storeName of db.objectStoreNames) {
            const allObjects = [];
            // transaction
            //     .objectStore(storeName)
            //     .openCursor()
            const objectStore = transaction.objectStore(storeName);
            const keyPath = objectStore.keyPath;

            const indices = [];
            const indexNames = objectStore.indexNames;
            for (let i = 0; i < indexNames.length; i++) {
                const index = objectStore.index(indexNames[i]);
                indices.push({
                    name: index.name,
                    keyPath: index.keyPath,
                    options: {
                        unique: index.unique,
                        multiEntry: index.multiEntry
                    }
                });
            }

            objectStore.openCursor().addEventListener('success', (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    // Cursor holds value, put it into store data
                    allObjects.push(cursor.value);
                    cursor.continue();
                } else {
                    // No more values, store is done
                    const dbStore = {
                        "name": storeName,
                        "keyPath": keyPath,
                        "indices": indices,
                        "values": allObjects
                    };
                    dbStores.push(dbStore);

                    // Last store was handled
                    if (db.objectStoreNames.length === dbStores.length) {
                        callback(dbStores);
                        return;
                    }
                }
            });
        }
    }
};

window.indexedDB.databases().then((dbs) => {

    const pushDbsToResultLoop = (result, dbs, callback) => {
        if (dbs.length === 0) {
            callback(result);
        }
        else {
            const curDb = dbs.shift();
            const curDbName = curDb.name;
            const curDbVersion = curDb.version;

            openDb(curDbName, (callbackDb) => {
                if (callbackDb !== null) {

                    getAllObjectStores(callbackDb, (callbackDbObjectStores) => {
                        result.push({
                            "dbName": curDbName,
                            "dbVersion": curDbVersion,
                            "dbObjectStores": callbackDbObjectStores
                        });
                    });
                }
                pushDbsToResultLoop(result, dbs, callback);
            });
        }
    };

    pushDbsToResultLoop([], dbs, (callbackResult) => {
        console.log('----Ergebnis IndexedDB-Export----');
        console.log(callbackResult);
        selenium_callback(callbackResult);
    });
})