const selenium_callback = arguments[arguments.length - 1];

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
//             console.log('----IndexedDB-Löschung abgeschlossen----');
//             callback(true);
//         });
//     });
// };

const createDb = ({ dbName, dbVersion, dbObject }, callback) => {

    const importedObjectStoreNames = Object.keys(dbObject);
    const DBOpenRequest = window.indexedDB.open(dbName, dbVersion);

    DBOpenRequest.onerror = (event) => {
        console.warn(`IndexedDB "${dbName}" konnte nicht erstellt werden.`);
        callback(null);
    };

    DBOpenRequest.onupgradeneeded = (event) => {
        console.log('---onupgradeneeded---');
        for (const importedObjectStoreName of importedObjectStoreNames) {
            db.createObjectStore(importedObjectStoreName);
        }
    }

    DBOpenRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${dbName}" erfolgreich erstellt.`);
        let db = DBOpenRequest.result;

        const addItems = (objectStoreName, newItems, callbackAdd) => {
            // open a read/write db transaction, ready for adding the data
            // const transaction = db.transaction([objectStoreName], "readwrite");
            const transaction = db.transaction([objectStoreName], "readwrite");
            // report on the success of the transaction completing, when everything is done
            transaction.oncomplete = (event) => {
                // console.log(`Alle Items von "${objectStoreName}" erfolgreich hinzugefügt.`);
                callbackAdd(true);
            };
            transaction.onerror = (event, source, lineno, colno, error) => {
                console.warn(`Error beim hinzufügen der Items von "${objectStoreName}": ${error}`);
                callbackAdd(false);
            };

            // create an object store on the transaction
            const objectStore = transaction.objectStore(objectStoreName);

            for (const newItem of newItems) {

                // https://www.freecodecamp.org/news/a-quick-but-complete-guide-to-indexeddb-25f030425501/
                // https://stackoverflow.com/questions/73967282/how-to-use-indexeddb-with-selenium-in-javascript


                const putRequest = objectStore.put(newItem,);
                putRequest.onsuccess = (event) => {
                    // console.log("Item hinzugefügt.", putRequest.result);
                    // console.log(newItem);
                };
                putRequest.onerror = (event, source, lineno, colno, error) => {
                    console.warn(`Error beim Hinzufügen (Put) eines Items: ${error}`)
                    console.log(newItem);
                }

                // const objectStoreRequest = objectStore.add(newItem);
                // objectStoreRequest.onsuccess = (event) => {
                //     // console.log("Item hinzugefügt.", objectStoreRequest.result);
                //     // console.log(newItem);
                // };
                // objectStoreRequest.onerror = (event, source, lineno, colno, error) => {
                //     console.warn(`Error beim Hinzufügen Add) eines Items: ${error}`)
                //     console.log(newItem);
                // }
            }
        };


        const addObjectStoreLoop = (objectStoreNames, callbackLoop) => {
            if (objectStoreNames.length === 0) {
                callbackLoop(true);
                return;
            }
            const curObjectStoreName = objectStoreNames.shift();
            const itemsToAdd = dbObject[curObjectStoreName];
            addItems(curObjectStoreName, itemsToAdd, (isSuccessful) => {
                addObjectStoreLoop(objectStoreNames, callbackLoop);
            });

        };

        addObjectStoreLoop(importedObjectStoreNames, (isSuccessful) => {
            callback(db);
        });
    };
};

// const setDbFromObject = (db, importedDb, callback) => {

//     const importedObjectStoreNames = Object.keys(importedDb);
//     // const transaction = db.transaction(db.objectStoreNames, 'readwrite');
//     const transaction = db.transaction(importedObjectStoreNames, 'readwrite');


//     transaction.oncomplete = (event) => {
//         console.log("Transaction abgeschlossen.");
//         for (const importedStoreName of importedObjectStoreNames) {
//             let count = 0;
//             for (const toAdd of importedDb[importedStoreName]) {
//                 const request = transaction.objectStore(importedStoreName).add(toAdd);
//                 request.addEventListener('success', () => {
//                     count++;
//                     if (count === importedDb[importedStoreName].length) {
//                         // Added all objects for this store
//                         delete importedDb[importedStoreName];
//                         if (Object.keys(importedDb).length === 0) {
//                             // Added all object stores
//                             callback(true);
//                         }
//                     }
//                 });
//             }
//         }
//     };

//     transaction.onerror = (event) => {
//         console.log("Transaction fehlgeschlagen.");
//         callback(false);
//     };

// };

const restoreDbsLoop = (indexed_db, callback) => {
    if (indexed_db.length === 0) {
        callback(true);
        return;
    }
    const cur_indexed_db = indexed_db.shift();
    createDb(cur_indexed_db, (createdDb) => {

        restoreDbsLoop(indexed_db, callback);

        // if (createdDb) {
        //     setDbFromObject(createdDb, cur_indexed_db.dbObject, (isSuccessful) => {

        //         restoreDbsLoop(indexed_db, callback);

        //     });
        // }
        // else {
        //     restoreDbsLoop(indexed_db, callback);
        // }
    });
};




const indexed_db = arguments[0];
restoreDbsLoop(indexed_db, (isDone) => {
    console.log('Alle Einträge der IndexedDB eingelesen.');
    selenium_callback(true);
});


// clearDbs((dbsCleared) => {
//     console.log('Alle Einträge der IndexedDB gelöscht.');
//     const indexed_db = arguments[0];
//     restoreDbsLoop(indexed_db, (isDone) => {
//         console.log('Alle Einträge der IndexedDB eingelesen.');
//         selenium_callback(true);
//     });
// });