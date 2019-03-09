//- ----------------------------------
//- 💥 DISPLACY ENT
//- ----------------------------------

'use strict';

class displaCyENT {
    constructor (api, options) {
        this.api = api;
        this.container = document.querySelector(options.container || '#displacy');

        this.defaultText = options.defaultText || "Create serverless logic with Azure Functions and event hubs";
        this.defaultModel = options.defaultModel || 'en';
        this.defaultEnts = options.defaultEnts || ['azure_service'];

        this.onStart = options.onStart || false;
        this.onSuccess = options.onSuccess || false;
        this.onError = options.onError || false;
        this.onRender = options.onRender || false;

    }

    parse(text = this.defaultText, model = this.defaultModel, ents = this.defaultEnts) {
        if(typeof this.onStart === 'function') this.onStart();

        return fetch(this.api, {
            method: "POST", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", // no-cors, cors, *same-origin
            cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ documents: [{id: "1", text }]}), // body data type must match "Content-Type" header
        })
        .then(response => response.json())
        .then(data => {
            const documentsRes = data.documents
            const cloudServices = documentsRes[0].cloudServices
            if(typeof this.onSuccess === 'function') this.onSuccess();
            this.render(text, cloudServices || [], ents);
        })
        .catch(error => {
            console.error('ERROR: ', error)
            if(typeof this.onError === 'function') this.onError(error);
        })
        // xhr.open('POST', this.api, true);
        // xhr.setRequestHeader('Content-type', 'application/json');
        // xhr.onreadystatechange = () => {
        //     if(xhr.readyState === 4 && xhr.status === 200) {
        //         const documentsRes = JSON.parse(xhr.responseText).documents
        //         const cloudServices = documentsRes[0].cloudServices
        //         if(typeof this.onSuccess === 'function') this.onSuccess();
        //         this.render(text, cloudServices || [], ents);
        //     }

        //     else if(xhr.status !== 200) {
        //         if(typeof this.onError === 'function') this.onError(xhr.statusText);
        //     }
        // }

        // xhr.onerror = () => {
        //     xhr.abort();
        //     if(typeof this.onError === 'function') this.onError();
        // }

        // xhr.send(JSON.stringify({ documents: [{id: "1", text }]}));
    }

    render(text, cloudServices, ents) {
        console.log('SPANS: ', cloudServices)
        this.container.innerHTML = '';
        let offset = 0;

        cloudServices.forEach(({ serviceUri, matches }) => {
            matches.forEach(({label, start, end}) => {
                const entity = text.slice(start, end);
                const fragments = text.slice(offset, start).split('\n');
    
                fragments.forEach((fragment, i) => {
                    this.container.appendChild(document.createTextNode(fragment));
                    if(fragments.length > 1 && i != fragments.length - 1) this.container.appendChild(document.createElement('br'));
                });
    
                if(ents.includes(label.toLowerCase())) {
                    const mark = document.createElement('a');
                    mark.setAttribute('href', serviceUri)
                    mark.setAttribute('target', '_blank')
                    mark.setAttribute('data-entity', label.toLowerCase());
                    mark.appendChild(document.createTextNode(entity));
                    this.container.appendChild(mark);
                }
    
                else {
                    this.container.appendChild(document.createTextNode(entity));
                }
    
                offset = end;
            })
            
        });

        this.container.appendChild(document.createTextNode(text.slice(offset, text.length)));

        console.log(`%c💥  HTML markup\n%c<div class="entities">${this.container.innerHTML}</div>`, 'font: bold 16px/2 arial, sans-serif', 'font: 13px/1.5 Consolas, "Andale Mono", Menlo, Monaco, Courier, monospace');

        if(typeof this.onRender === 'function') this.onRender();
    }
}
