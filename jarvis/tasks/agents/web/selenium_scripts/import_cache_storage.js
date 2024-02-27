const cachesToImport = arguments[0];
const selenium_callback = arguments[arguments.length - 1];


// Put item into a cache object
const putCacheItem = (openedCache, cacheItem, callback) => {

    if (cacheItem.value === null || cacheItem.value === undefined) {
        // There is no need to put an item with no value, so return immediately
        callback(false);
        return;
    }

    // Create a "fake" response containing the data to import
    const body = JSON.stringify(cacheItem.value);
    const contentType = cacheItem.contentType || "application/json";
    const headers = { "Content-Type": contentType };
    const options = { status: 200, statusText: "", headers: headers };
    const response = new Response(body, options);

    openedCache.put(cacheItem.url, response).then(() => callback(true));
    // openedCache.put(cacheItem.url, response);
    // callback(true);
};

// Put multiple items into a cache object
const importCache = (cacheToImport, callback) => {

    const cacheName = cacheToImport.cacheName;
    const cacheItems = cacheToImport.cacheItems;

    if (cacheItems.length === 0) {
        // There are no items in the cache, so there's no need to create it
        callback(false);
        return;
    }

    // Create cache to write entries/items into it
    window.caches.open(cacheName).then((openedCache) => {
        // openedCache is a new cache (object) named with cacheName (if the specified cache already exists, the items are added there)

        let processedCount = 0;
        for (const cacheItem of cacheItems) {
            putCacheItem(openedCache, cacheItem, (cbIsPut) => {
                processedCount++;
                if (processedCount === cacheItems.length) {
                    console.log(`Einlesen des Caches "${cacheName}" abgeschlossen.`);
                    callback(true);
                }
            });
        }
    });
};



if (!cachesToImport || cachesToImport.length === 0) {
    selenium_callback(false);
}
else {
    let importedCachesCount = 0;
    for (const cacheToImport of cachesToImport) {
        importCache(cacheToImport, (cbIsImported) => {
            importedCachesCount++;
            if (importedCachesCount === cachesToImport.length) {
                console.log(`Alle Caches eingelesen.`);
                selenium_callback(true);
            }
        });
    }
}