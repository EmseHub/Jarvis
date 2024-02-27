const selenium_callback = arguments[arguments.length - 1];


// Read a specific cache entry/item of a cache object
const getCacheItem = (openedCache, cacheItemRequest, callback) => {
    const cacheItem = { url: cacheItemRequest.url, value: null, contentType: "" };
    openedCache.match(cacheItemRequest)
        // match() behaves similarly to fetch() here
        .then((response) => {
            if (response) {
                const contentType = response.headers.get("content-type");
                // For now, only JSON is supported (nothing like "image/png" etc.)
                if (contentType && contentType.toLowerCase() === "application/json") {
                    cacheItem.contentType = contentType;
                    return response.json();
                }
                // if () {
                //     response.arrayBuffer();
                //     return new Uint8Array(buffer);
                // }
            }
            return null;
        })
        .then((data) => {
            cacheItem.value = data;
            callback(cacheItem);
        });
};


// Read all entries of a cache object
const getCacheItems = (cacheName, callback) => {
    // Open cache to loop through its entries/items
    window.caches.open(cacheName).then((openedCache) => {
        // openedCache is the cache (object) matching the cacheName (in case the specified cache does not exist, a new cache would be created)
        openedCache.keys().then((cacheItemRequests) => {
            // cacheItemRequests is an array of requests that each refer to a specific item of the opened cache
            const cacheItems = [];
            if (cacheItemRequests.length === 0) {
                // There are no items in the opened cache, so return immediately
                callback(cacheItems);
                return;
            }
            // Call all requests
            let processedCount = 0;
            for (const cacheItemRequest of cacheItemRequests) {
                getCacheItem(openedCache, cacheItemRequest, (cbCacheItem) => {
                    processedCount++;
                    if (cbCacheItem.value !== null && cbCacheItem.value !== undefined) {
                        cacheItems.push(cbCacheItem);
                    }
                    // If all items of the cache have been processed, return the result as array
                    if (processedCount === cacheItemRequests.length) {
                        callback(cacheItems);
                    }
                });
            }
        });
    });
};


// Read names of all caches of the website 
const getCacheNames = (callback) => {
    window.caches.keys().then((cacheNames) => callback(cacheNames));
    // cacheNames is an array of the names of all the caches in the cache storage (window.caches.keys() is not to be confused with someOpenedCache.keys())
};


// Call functions to export cache
const exportedCaches = [];

getCacheNames((cbCacheNames) => {

    if (cbCacheNames.length === 0) {
        console.log(`Keine Caches gefunden.`);
        selenium_callback(exportedCaches);
        return;
    }

    for (const cacheName of cbCacheNames) {
        getCacheItems(cacheName, (cbCacheItems) => {
            exportedCaches.push({ cacheName: cacheName, cacheItems: cbCacheItems });
            if (exportedCaches.length === cbCacheNames.length) {
                console.log(`Alle Caches exportiert.`);
                console.log(exportedCaches);
                selenium_callback(exportedCaches);
            }
        });
    }
});






// window.caches.keys().then((cacheNames) => {
//     // cacheNames is an array of the names of all the caches in the cache storage
//     for (const cacheName of cacheNames) {
//         // Open cache to loop through its entries/items
//         caches.open(cacheName).then((openedCache) => {
//             // openedCache is the cache (object) matching the cacheName (in case the specified cache does not exist, a new cache would be created)
//             openedCache.keys().then((cacheItemRequests) => {
//                 // cacheItemRequests is an array of requests that each refer to a specific item of the current cache
//                 for (const itemRequest of cacheItemRequests) {

//                     caches.match(itemRequest)
//                         .then((response) => {

//                             console.log(response);
//                             if (response) {
//                                 const contentType = response.headers.get("content-type");
//                                 console.log(contentType);
//                                 return response.json();
//                             }
//                             return null;
//                         })
//                         .then((data) => {
//                             console.log(data);
//                         });

//                 }

//             });
//         });
//     }
// });


