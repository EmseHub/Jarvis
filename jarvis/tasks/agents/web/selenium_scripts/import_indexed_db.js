const deleteDb = (name, callback) => {
    const DBDeleteRequest = window.indexedDB.deleteDatabase(name);
    DBDeleteRequest.onerror = (event) => {
        console.warn(`IndexedDB "${name}" konnte nicht gelöscht werden.`);
        callback(false);
    };
    DBDeleteRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${name}" erfolgreich gelöscht.`);
        callback(true);
    };
}

const clearDbs = (callback) => {
    window.indexedDB.databases().then((dbs) => {
        const clearDbsLoop = (dbs, callbackLoop) => {
            if (dbs.length === 0) {
                callbackLoop(true);
                return;
            }
            const curDb = dbs.shift();
            deleteDb(curDb.name, (isSuccessful) => {
                clearDbsLoop(dbs, callbackLoop);
            });
        };

        clearDbsLoop(dbs, (callbackLoopResult) => {
            console.log('----IndexedDB-Löschung abgeschlossen----');
            callback(true);
        });
    });
};

const createDb = (name, version, callback) => {
    const DBOpenRequest = window.indexedDB.open(name, version);
    DBOpenRequest.onerror = (event) => {
        console.warn(`IndexedDB "${name}" konnte nicht erstellt werden.`);
        callback(null);
    };
    DBOpenRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${name}" erfolgreich erstellt.`);
        const db = DBOpenRequest.result;
        callback(db);
    };
};

const setDbFromObject = (db, importedDb, callback) => {

    const transaction = db.transaction(db.objectStoreNames, 'readwrite');

    objectStoreNames = Object.keys(importedDb);

    for (const storeName of objectStoreNames) {
        let count = 0;
        for (const toAdd of importedDb[storeName]) {
            const request = transaction.objectStore(storeName).add(toAdd);
            request.addEventListener('success', () => {
                count++;
                if (count === importedDb[storeName].length) {
                    // Added all objects for this store
                    delete importedDb[storeName]
                    if (Object.keys(importedDb).length === 0) {
                        // Added all object stores
                        callback(true);
                        return;
                    }
                }
            });
        }
    }
};

const restoreDbsLoop = (dbs, callback) => {
    if (dbs.length === 0) {
        callback(true);
        return;
    }
    const curDb = dbs.shift();
    createDb(curDb.name, curDb.version, (createdDb) => {
        if (createdDb) {
            setDbFromObject(createdDb, curDb.dbObject, (isSuccessful) => {

                restoreDbsLoop(dbs, callback);

            });
        }
        else {
            restoreDbsLoop(dbs, callback);
        }
    });
};


clearDbs((dbsCleared) => {
    const indexed_db = arguments[0];
    restoreDbsLoop(indexed_db.map(db => db.dbObject), (isDone) => {
        console.log('Alle Einträge der IndexedDB gelöscht.');
    });
});







