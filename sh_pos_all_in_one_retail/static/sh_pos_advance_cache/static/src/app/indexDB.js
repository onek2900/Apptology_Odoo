(function(){
    function waitIndexDb() {

        if (!window.indexedDB) {
            console.log(`Your browser doesn't support IndexedDB`);
            return;
        }
        const indexedDB = window.indexedDB
    
        var indexedDB_dic = {
    
            create_objectstore: function (objectstore) {
    
                const request = indexedDB.open('Softhealer_pos', 1);
    
                request.onerror = function (event) {
                    console.error(`Database error: ${event.target.errorCode}`);
                };
    
                request.onupgradeneeded = function (event) {
    
                    let db = event.target.result;
    
                    let store = db.createObjectStore('Products',
                        { keyPath: "id" }
                    );
                    let store1 = db.createObjectStore('Customers',
                        { keyPath: "id" }
                    );
                }
                return request
            },
    
            save_data: function (objectstore, data_list) {
                var self = this;
    
                this.create_objectstore(objectstore).onsuccess = function (ev) {
    
                    var db = ev.target.result;
    
                    // create a new transaction
                    var txn = db.transaction(objectstore, 'readwrite');
    
                    // get the Contacts object store
                    var store = txn.objectStore(objectstore);
    
                    for (const each_data of data_list) {
                        if (objectstore === 'Products') {
                            if (each_data['pos']) {
                                delete each_data['pos'];
                            }
                        }
                        var query = store.put(each_data);
    
                        // handle success case
                        query.onsuccess = function (event) {
                            // console.log(event);
                        };
    
                        // handle the error case
                        query.onerror = function (event) {
                            console.log(event.target.errorCode);
                        }
    
                        // close the database once the 
                        // transaction completes
                        txn.oncomplete = function () {
                            db.close();
                        };
                    }

                }
            },
            get_all: function (objectstore) {
                var self = this;
                var def = new $.Deferred();
    
                this.create_objectstore(objectstore).onsuccess = function (ev) {
                    
                    var db = ev.target.result;
    
                    // create a new transaction
                    var txn = db.transaction(objectstore, 'readwrite');
                    
                    // get the Contacts object store
                    var store = txn.objectStore(objectstore);
                    
                    store.getAll().onsuccess = function (event) {
                        let cursor = event.target.result;
                        def.resolve(cursor);
                    };
                    
                    
                };
                return def;
            },
    
            get_by_id: function (objectstore, key) {
    
                var self = this;
                var def = new $.Deferred();
    
                this.create_objectstore(objectstore).onsuccess = function (ev) {
    
                    var db = ev.target.result;
    
                    // create a new transaction
                    var txn = db.transaction(objectstore, 'readwrite');
    
                    // get the Contacts object store
                    var store = txn.objectStore(objectstore);
    
                    store.get(key).onsuccess = function (event) {
                        let cursor = event.target.result;
                        def.resolve(cursor);
                    };
    
    
                };
                return def;
            },
            delete_item: function (objectstore, key) {
    
                var self = this;
                var def = new $.Deferred();
    
                this.create_objectstore(objectstore).onsuccess = function (ev) {
    
                    var db = ev.target.result;
    
                    // create a new transaction
                    var txn = db.transaction(objectstore, 'readwrite');
    
                    // get the Contacts object store
                    var store = txn.objectStore(objectstore);
    
                    store.delete(key).onsuccess = function (event) {
                        let cursor = event.target.result;
                        def.resolve(cursor);
                    };
    
    
                };
                return def;
            },
        }
    
        return indexedDB_dic;
    }
    window.waitIndexDb = waitIndexDb;  

})();
