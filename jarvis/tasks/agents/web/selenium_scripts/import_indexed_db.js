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

const createDb = ({ dbName, dbVersion, dbObjectStores }, callback) => {

    const DBOpenRequest = window.indexedDB.open(dbName, dbVersion);

    DBOpenRequest.onerror = (event) => {
        console.warn(`IndexedDB "${dbName}" konnte nicht erstellt werden.`);
        console.warn(error);
        callback(null);
    };

    // Neue DB erstellt oder Version einer bestehenden DB geändert
    DBOpenRequest.onupgradeneeded = (event) => {
        // console.log('---onupgradeneeded---');

        // Neue DB in Konstante speichern
        const db = DBOpenRequest.result;

        const sample_export = [
            {
                "dbName": "cars",
                "dbVersion": 2,
                "dbObjectStores": [
                    {
                        "name": "some_table_name",
                        "keyPath": "sth",
                        // "primaryKeyPath": "some_id_or_key",
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
                        "values": [
                            {
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
                            },
                        ]
                    },
                ]
            },
        ];

        // Object Stores in DB anlegen (ein Object Store entspricht einer Tabelle)
        for (const importedObjectStore of dbObjectStores) {

            const name = importedObjectStore["name"];
            const keyPath = importedObjectStore["keyPath"];
            // keyPath entspricht dem Primary Key


            const store = (keyPath)
                ? db.createObjectStore(name, { keyPath: keyPath })
                : db.createObjectStore(name);

            for (const index of importedObjectStore["indices"]) {
                store.createIndex(index["name"], index["keyPath"], index["options"]);
            }
        }
    }

    DBOpenRequest.onsuccess = (event) => {
        console.log(`IndexedDB "${dbName}" erfolgreich erstellt.`);

        const db = DBOpenRequest.result;

        const putItems = (objectStoreName, callbackAdd) => {

            const transaction = db.transaction([objectStoreName], "readwrite");

            transaction.oncomplete = (event) => {
                // console.log(`Alle Items von "${objectStoreName}" erfolgreich hinzugefügt.`);
                callbackAdd(true);
            };
            transaction.onerror = (event, source, lineno, colno, error) => {
                console.warn(`Error beim hinzufügen der Items von "${objectStoreName}"`);
                console.warn(event);
                callbackAdd(false);
            };

            const objectStore = transaction.objectStore(objectStoreName);

            // const importedObjectStore = dbObjectStores[objectStoreName];
            const importedObjectStore = dbObjectStores.find(os => os.name === objectStoreName);

            for (const index of importedObjectStore["indices"]) {
                const cur = objectStore.index(index["name"]);
            }

            for (const item of importedObjectStore["values"]) {

                // https://www.freecodecamp.org/news/a-quick-but-complete-guide-to-indexeddb-25f030425501/
                // https://stackoverflow.com/questions/73967282/how-to-use-indexeddb-with-selenium-in-javascript

                // ANOTHER CONNECTION WANTS TO DELETE WAWC... ERROR

                const putRequest = objectStore.put(item);
                putRequest.onsuccess = (event) => {
                    // console.log("Item hinzugefügt.", putRequest.result);
                    // console.log(newItem);
                };
                putRequest.onerror = (event) => {
                    console.warn(`Error beim Hinzufügen (Put) eines Items: ${item}`);
                    console.warn(event);
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
            putItems(curObjectStoreName, (isSuccessful) => {
                addObjectStoreLoop(objectStoreNames, callbackLoop);
            });

        };

        addObjectStoreLoop(dbObjectStores.map(os => os.name), (isSuccessful) => {
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
        //     setDbFromObject(createdDb, cur_indexed_db.dbObjectStores, (isSuccessful) => {

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