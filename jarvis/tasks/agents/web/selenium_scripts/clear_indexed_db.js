window.indexedDB.databases().then((dbs) => {
    for (const db of dbs) {
        window.indexedDB.deleteDatabase(db.name);
    }
}).then(() => {
    console.log('Alle Einträge der IndexedDB gelöscht.');
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