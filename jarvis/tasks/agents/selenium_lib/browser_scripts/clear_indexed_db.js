(() => {
    window.indexedDB.databases().then((dbs) => {
        for (const db of dbs) {
            window.indexedDB.deleteDatabase(db.name);
        }
    }).then(() => {
        console.log("All IndexedDB entries deleted.");
    });



    // const clearDb = (db, callback) => {
    //     const transaction = db.transaction(db.objectStoreNames, 'readwrite');
    //     transaction.addEventListener('error', callback(false));

    //     let count = 0;
    //     for (const storeName of db.objectStoreNames) {
    //         transaction
    //             .objectStore(storeName).clear().addEventListener('success', () => {
    //                 count++
    //                 if (count === db.objectStoreNames.length) {
    //                     // Cleared all object stores
    //                     callback(true);
    //                     return;
    //                 }
    //             });
    //     }
    // };

    // window.indexedDB.databases().then((dbs) => {

    //     const clearDbs = (dbs, callback) => {
    //         if (dbs.length === 0) {
    //             callback(true);
    //             return;
    //         }
    //         const curDb = dbs.shift();
    //         openDb(curDb, (isDone) => {
    //             clearDbs(dbs, callback);
    //         });
    //     };

    //     clearDbs(dbs, () => { console.log('Alle Einträge der IndexedDB gelöscht.'); });
    // });


    // ------OR------

    // const deleteDb = (name, callback) => {
    //     const DBDeleteRequest = window.indexedDB.deleteDatabase(name);
    //     DBDeleteRequest.onerror = (event) => {
    //         console.warn(`IndexedDB "${name}" konnte nicht gelöscht werden.`);
    //         callback(false);
    //     };
    //     DBDeleteRequest.onsuccess = (event) => {
    //         console.log(`IndexedDB "${name}" erfolgreich gelöscht.`);
    //         callback(true);
    //     };
    // }

    // const clearDbs = (callback) => {
    //     window.indexedDB.databases().then((dbs) => {
    //         const clearDbsLoop = (dbs, callbackLoop) => {
    //             if (dbs.length === 0) {
    //                 callbackLoop(true);
    //                 return;
    //             }
    //             const curDb = dbs.shift();
    //             deleteDb(curDb.name, (isSuccessful) => {
    //                 clearDbsLoop(dbs, callbackLoop);
    //             });
    //         };

    //         clearDbsLoop(dbs, (callbackLoopResult) => {
    //             console.log("Löschen der IndexedDB abgeschlossen.");
    //             callback(true);
    //         });
    //     });
    // };
})();