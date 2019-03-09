//- ----------------------------------
//- 💥 DISPLACY DEMO
//- ----------------------------------

'use strict';

{
    const defaultText = "Create serverless logic with Azure Functions, event hubs, and Cosmos DB";

    const defaultEnts = ['azure_service'];
    const defaultModel = 'en';

    const loading = () => document.body.classList.toggle('loading');
    const onError = (err) => $('#error').style.display = 'block';
    const updateHTML = () => $('#html').value = `<div class="entities">${$('#displacy').innerHTML}</div>`;

    const displacy = new displaCyENT(api, {
        container: '#displacy',
        defaultText: defaultText,
        defaultModel: defaultModel,
        defaultEnts: defaultEnts,
        onStart: loading,
        onSuccess: loading,
        // onRender: updateHTML,
        onError: onError
    });


    // UI

    const $ = document.querySelector.bind(document);
    const $$ = document.querySelectorAll.bind(document);


    // First Run

    document.addEventListener('DOMContentLoaded', () => {
        const text = getQueryVar('text') || defaultText;
        const model = getQueryVar('model') || defaultModel;
        const ents = (getQueryVar('ents')) ? getQueryVar('ents').split(',') : defaultEnts;

        if(text) updateView(text, model, ents);
        displacy.parse(text, model, ents);
        $('#css').value = renderCSS('displacy-ent.css');
    });

    // Run Demo

    const run = (
        text = $('#input').value || defaultText,
        ents = [...$$('[name="ents"]:checked')].map(ent => ent.value),
        model = $('[name="model"]:checked').value || defaultModel ) => {
            displacy.parse(text, model, ents);
            updateView(text, model, ents);
            updateURL(text, model, ents);
    }


    // UI Event Listeners

    $('#submit').addEventListener('click', ev => run());
    $('#input').addEventListener('keydown', ev => (event.keyCode == 13) && run());

    const navDisplay = (e) => {
        e.target.addClass('is-active')
        e.target.addClass('u-strong')
        // event.target.addClass('is-active')
        // event.target.addClass('u-strong')
    }
    $('li.demo').addEventListener('click', ev => navDisplay)
    $('li.api-docs').addEventListener('click', ev => navDisplay)


    // Update View

    const updateView = (text, model, ents) => {
        $('#input').value = text;
        ents.forEach(ent => $(`[value="${ent}"]`).checked = true);
        $(`[value="${model}"]`).checked = true;
    }


    // Update URL

    const updateURL = (text, model, ents) => {
        const params = { text, ents, model };
        const url = Object.keys(params).map(param => `${param}=${encodeURIComponent(params[param])}`);
        history.pushState(params, null, '?' + url.join('&'));
    }


    // Render CSS from stylesheet

    const renderCSS = (filename) => {
        let rules = [];
        for(let sheet of document.styleSheets) if(sheet.href.indexOf(filename) != -1) for(let rule of sheet.cssRules) rules.push(rule.cssText);
        return rules.join('')
            .replace(/;((?! }))/g, ';\n' + '    ')
            .replace(/\{/g, '{\n' + '    ')
            .replace(/\}/g, '\n}\n\n')
            .trim()
    }


    // Get URL Query Variables

    const getQueryVar = (key) => {
       const query = window.location.search.substring(1);
       const params = query.split('&').map(param => param.split('='));

       for(let param of params) if(param[0] == key) return decodeURIComponent(param[1]);
       return false;
    }
}
