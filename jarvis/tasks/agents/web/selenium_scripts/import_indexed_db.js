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

    // onupgradeneeded --> Ausgelöst, wenn neue DB erstellt oder Version einer bestehenden DB geändert
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

        // Object Stores in DB anlegen (ein Object Store entspricht einer Tabelle)
        for (const importedObjectStore of dbObjectStores) {

            const name = importedObjectStore["name"];
            const keyPath = importedObjectStore["keyPath"];
            // const autoIncrement = importedObjectStore["autoIncrement"];

            // keyPath entspricht dem, was in anderen DB der Primary Key ist
            // autoIncrement immer auf false, um eigenen Wert zuzuweisen
            const options = { autoIncrement: false };
            if (keyPath !== null && keyPath !== undefined) { options.keyPath = keyPath; }

            const store = db.createObjectStore(name, options);

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

            const importedObjectStore = dbObjectStores.find(os => os.name === objectStoreName);
            const keyPath = importedObjectStore["keyPath"];


            // Indices für Queries definieren
            // for (const index of importedObjectStore["indices"]) {
            //     const cur = objectStore.index(index["name"]);
            // }

            for (const item of importedObjectStore["items"]) {

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


        const populateObjectStoreLoop = (objectStoreNames, callbackLoop) => {
            if (objectStoreNames.length === 0) {
                callbackLoop(true);
                return;
            }
            const curObjectStoreName = objectStoreNames.shift();
            putItems(curObjectStoreName, (isSuccessful) => {
                populateObjectStoreLoop(objectStoreNames, callbackLoop);
            });

        };

        populateObjectStoreLoop(dbObjectStores.map(os => os.name), (isSuccessful) => {
            db.close();
            callback(db);
        });
    };
};


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