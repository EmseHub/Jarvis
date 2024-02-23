const selenium_callback = arguments[arguments.length - 1];

const openDb = (name, callback) => {
    const DBOpenRequest = window.indexedDB.open(name);
    DBOpenRequest.onerror = (event) => {
        console.warn(`IndexedDB "${name}" konnte nicht geladen werden.`);
        callback(null);
    };

    DBOpenRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${name}" erfolgreich geladen.`);
        const db = DBOpenRequest.result;
        console.log(db);
        callback(db);
    };
};

const getObjectFromDb = (db, callback) => {
    const dbObject = {};
    if (db.objectStoreNames.length === 0) {
        callback(dbObject);
    }
    else {
        const transaction = db.transaction(db.objectStoreNames, 'readonly');
        for (const storeName of db.objectStoreNames) {
            const allObjects = [];
            transaction
                .objectStore(storeName)
                .openCursor()
                .addEventListener('success', (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        // Cursor holds value, put it into store data
                        allObjects.push(cursor.value);
                        cursor.continue();
                    } else {
                        // No more values, store is done
                        dbObject[storeName] = allObjects;

                        // Last store was handled
                        if (db.objectStoreNames.length === Object.keys(dbObject).length) {
                            callback(dbObject);
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

                    getObjectFromDb(callbackDb, (callbackDbAsObject) => {
                        result.push({
                            dbName: curDbName,
                            dbVersion: curDbVersion,
                            dbObject: callbackDbAsObject
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