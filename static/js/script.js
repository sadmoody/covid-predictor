var this_js_script = $('script[src*=somefile]');
var STATIC_URL = this_js_script.attr('static-url');
if (typeof STATIC_URL === "undefined" ) {
    var STATIC_URL = 'https://cdn.jsdelivr.net/gh/sadmoody/covid-predictor@latest/static/';
}

const CONTAINER = document.querySelector('#country-container');
let USER_COLOR_MODE = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
const dark_mode_button = document.querySelector('#dark-mode-button');
dark_mode_button.addEventListener('click', () => {
    USER_COLOR_MODE = !USER_COLOR_MODE;
    update_color_mode(USER_COLOR_MODE);
})

const update_color_mode = (isDark) => {
    const dark_mode_badge_icon = dark_mode_button.querySelector('.nes-badge__badge');
    const containers = document.querySelectorAll('.nes-container');
    const selects = document.querySelectorAll('.nes-select');

    if (isDark) {
        document.body.classList.add('dark');
        dark_mode_badge_icon.innerText = 'on';
        const addDarkClass = (el) => {
            el.classList.add('is-dark');
        }
        
        containers.forEach(addDarkClass);
        selects.forEach(addDarkClass);
    } else {
        document.body.classList.remove('dark');
        dark_mode_badge_icon.innerText = 'off';
        
        const removeDarkClass = (el) => {
            el.classList.remove('is-dark');
        }
        
        containers.forEach(removeDarkClass);
        selects.forEach(removeDarkClass);
    }
}

if (USER_COLOR_MODE) {
    update_color_mode(true);
}    

//TODO: Pool audio objects so they can be played in parallel
//          create new object if all current objects are busy
const confirmed_audio = STATIC_URL + "sounds/case.mp3";
var confirmed_audio_pool = [new Howl({src: [confirmed_audio], volume:0.5})];
const death_audio = STATIC_URL + "sounds/death.mp3";
var death_audio_pool = [new Howl({src: [death_audio], volume:0.5})];

var soundEnabled = !(window.localStorage.getItem('soundEnabled') == 'false');
var unmuteImage = STATIC_URL + "images/ui/unmute.png";
var muteImage = STATIC_URL + "images/ui/mute.png";
window.localStorage.setItem('soundEnabled', soundEnabled.toString());

function playAudio(event){
    if (!soundEnabled)
        return;
    var ready_audio;
    if (event == 'confirmed') {
        for (var i = 0; i< confirmed_audio_pool.length; i++)
        {
            var element = confirmed_audio_pool[i];
            if (!element.playing) {
                ready_audio = element;
                break;
            }
        }
        if (ready_audio == null){
            ready_audio = new Howl({src: [confirmed_audio], volume:0.5})
            confirmed_audio_pool.push(ready_audio);
        }
    } else if (event == 'death') {
        for (var i = 0; i< death_audio_pool.length; i++)
        {
            var element = death_audio_pool[i];
            if (!element.playing) {
                ready_audio = element;
                break;
            }
        }
        if (ready_audio == null){
            ready_audio = new Howl({src: [death_audio], volume:0.5});
            death_audio_pool.push(ready_audio);
        }
    }
    ready_audio.play();
}


// wrapper for fetching data and returning it as JSON
const fetchJSON = async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

// get country meta information from `countries-list` npm package
const metaCountryInfo = async () => {
    // TODO; copy this file for local consumption, maybe?
    const information = await fetchJSON('https://cdn.jsdelivr.net/npm/countries-list@2.5.4/dist/countries.emoji.json');
    return information
}

// get lookup table from source data's lookup table
const covidCountryLookUpTable = async () => {
    // I HATE THIS CSV CONVERSION CODE BUT I COPIED AND PASTED SO, EH!
    function CSVToJSON(csvData) {
        var data = CSVToArray(csvData);
        var objData = [];
        for (var i = 1; i < data.length; i++) {
            objData[i - 1] = {};
            for (var k = 0; k < data[0].length && k < data[i].length; k++) {
                var key = data[0][k];
                objData[i - 1][key] = data[i][k]
            }
        }
        var jsonData = JSON.stringify(objData);
        jsonData = jsonData.replace(/},/g, "},\r\n");
        return jsonData;
    }

    function CSVToArray(csvData, delimiter) {
        delimiter = (delimiter || ",");
        var pattern = new RegExp((
        "(\\" + delimiter + "|\\r?\\n|\\r|^)" +
        "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +
        "([^\"\\" + delimiter + "\\r\\n]*))"), "gi");
        var data = [[]];
        var matches = null;
        while (matches = pattern.exec(csvData)) {
            var matchedDelimiter = matches[1];
            if (matchedDelimiter.length && (matchedDelimiter != delimiter)) {
                data.push([]);
            }
            if (matches[2]) {
                var matchedDelimiter = matches[2].replace(
                new RegExp("\"\"", "g"), "\"");
            } else {
                var matchedDelimiter = matches[3];
            }
            data[data.length - 1].push(matchedDelimiter);
        }
        return (data);
    }

    const lookupTable = await fetch('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv');
    const text = await lookupTable.text();
    return JSON.parse(CSVToJSON(text));
}

// get our covid data
const covidFetch = async () => {
    return await fetchJSON(`/api/v1/countries/`);
}

// convert country names to a safe name to use as an unique identifier
const createSafeName = (name) => {
    return name
        .replace('*', '')
        .replace(',', '')
        .replace('(', '')
        .replace(')', '')
        .replace("'", '')
        .split(' ')
        .join('_')
        .toLowerCase();
}

const countryTemplate = document.querySelector('#country-template');
const createCountryElementAndAppend = (country) => {
    const { name, safe_name, emoji } = country;
    // clone template
    const el = countryTemplate.content.cloneNode(true);

    // find outer container div and set id
    const container = el.querySelector('.country');
    container.id = safe_name;
    
    // find emoji icon div and place content
    const emojiEl = el.querySelector('.country__info-emoji');
    emojiEl.innerHTML = "<img class=\"pixelated\" src=\"" + STATIC_URL + "images/flags/"+name.toLowerCase()+".png\" />";
    // find name icon div and place content
    const nameEl = el.querySelector('.country__info-name');
    nameEl.innerText = name;

    if (USER_COLOR_MODE) {
        container.classList.add('is-dark');
    }

    CONTAINER.appendChild(el);        
}

function updateCurrentRate(country, current_rate, rate_type='case') {
    const el = CONTAINER.querySelector('#' + country.toLowerCase());

    // set case values
    const caseMinuteEl = el.querySelector('.country__data-' + rate_type + '-minutes');
    const caseRateEl = el.querySelector('.country__data-' + rate_type + '-rate');
    const caseInbetweenEl = el.querySelector('.country__data-' + rate_type + '-inbetween');
     
    if ((current_rate <= 0) || (current_rate >= Infinity)) {
        // TODO: fix those that are negative numbers to remove this condition
        caseMinuteEl.innerText = '';
        caseRateEl.innerText = '';
        caseInbetweenEl.innerText = "Stable"
    } else if (current_rate <= (1000 * 100)) {
        caseMinuteEl.innerText = 1;
        caseRateEl.innerText = (current_rate / 1000).toFixed(2).toString() + ' seconds';
    } else {
        caseMinuteEl.innerText = '1';
        caseRateEl.innerText = `${Math.round(current_rate / 1000 / 60)} minutes`;
    }
}

window.onload = async function () {
    mounted();
    document.getElementById("sound-control").src = (soundEnabled ? unmuteImage : muteImage);
    const LOADING_BAR = document.querySelector('#loading-bar');
    const LOADING_TEXT = document.querySelector('#loading-text');
    const SORT_SELECTOR = document.querySelector('#sort-selector');
    /* 1. get list of countries, country info and lookup table info */
    LOADING_BAR.value = 10;
    LOADING_TEXT.innerText = 'loading...';
    const countries = await covidFetch();
    LOADING_BAR.value = 30;
    LOADING_TEXT.innerText = 'thinking...';
    const countryInfo = await metaCountryInfo();
    LOADING_BAR.value = 50;
    LOADING_TEXT.innerText = 'processing...';
    const lookupTableData = await covidCountryLookUpTable();

    LOADING_BAR.value = 70;
    LOADING_TEXT.innerText = 'doing.';
    /* 2. Compose the appropriate information together from both countries and countryInfo */
    const processedCountries = countries.map(country => {
        // set default return values
        const defaultContent = {
            ...country,
            safe_name: createSafeName(country.name),
            emoji: '⚑'
        };

        // gather calculations
        const calculations = processCountryData(country);

        // find country in lookup table, if available
        const lookupTable = lookupTableData.find(lt => lt.Country_Region === country.name);
        // set country code to gather additional info (i.e. emoji) else don't return anything
        const countryCode = lookupTable ? lookupTable.iso2 : '';
        // find actual country info from country code
        const foundCountryInfo = countryInfo[countryCode];
        // return combined values
        return {
            ...defaultContent,
            ...calculations,
            ...foundCountryInfo
        }
    })

    /* 3. Create country elements */
    LOADING_BAR.value = 85;
    LOADING_TEXT.innerText = 'doing..';
    processedCountries.forEach(createCountryElementAndAppend);

    /* 4. Wait for next dom render to attach bar */
    LOADING_BAR.value = 90;
    LOADING_TEXT.innerText = 'doing...';
    setTimeout(() => {
        for (let i = 0; i < processedCountries.length; i++) {
            const country = processedCountries[i];
            const countryEl = CONTAINER.querySelector(`#${country.safe_name}`);
            const casesEl = countryEl.querySelector('.country__data-cases');
            const casesTextEl = countryEl.querySelector('.country__data-cases-text');
            const deathsEl = countryEl.querySelector('.country__data-deaths');
            const deathsTextEl = countryEl.querySelector('.country__data-deaths-text');

            build_bar(casesEl, casesTextEl, country, 'case');
            build_bar(deathsEl, deathsTextEl, country, 'death');
        }

        sort_elements('caseRate', 'country-container', '.country-outer .country', depth=1, multiplier=1.0);

        LOADING_BAR.value = 100;
        SORT_SELECTOR.disabled = false;
        document.body.dataset.loading = "false";
    }, 0)
}

/**** Maths ****/
function poly_three(x, formula) {
    const { a, b, c, d } = formula;
    return a * Math.pow(x, 3) + b * Math.pow(x, 2)  + c * x + d;
}

function poly_three_dx(x, formula) {
    const { a, b, c } = formula;
    return 3 * a * Math.pow(x, 2) + 2 * b * x  + c;
}

function update_data_fields(country, current_count, current_rate, rate_type='case') {
    const el = CONTAINER.querySelector('#' + country.toLowerCase());
    el.dataset[rate_type + 'Count'] = current_count;
    el.dataset[rate_type + 'Rate'] = current_rate;
    el.dataset['name'] = country;
}

function processCountryData(country) {
    // Find difference in time between last dataset update and now
    var t_zero_array = country.t_zero.split('-').map(Number);
    var current_date = new Date().getTime();
    var t_zero = Date.UTC(t_zero_array[0], t_zero_array[1]-1, t_zero_array[2])
    // Represent time in decimal days from last dataset update
    var x = ((current_date - t_zero) / 1000 / 3600 / 24) - 1;
    // Get current number of cases by applying third order polynomial
    var current_cases = poly_three(x, country.confirmed_formula);
    // Get current fraction of cases (so that we can start our progress bar in the right place)
    var current_case_progress = current_cases % 1;
    // Period of new confirmed cases in ms
    var current_case_rate = 1000 / (poly_three_dx(x, country.confirmed_formula) / 24 / 3600);
    // Remaining time in progress bar until it reaches end of *current* case
    var case_finish_time = current_case_rate - current_case_progress * current_case_rate;

    // Get current number of cases by applying third order polynomial
    var current_deaths = poly_three(x, country.death_formula);
    // Get current fraction of cases (so that we can start our progress bar in the right place)
    var current_death_progress = current_deaths % 1;
    // Period of new confirmed cases in ms
    var current_death_rate = 1000 / (poly_three_dx(x, country.death_formula) / 24 / 3600);
    // Remaining time in progress bar until it reaches end of *current* case
    var death_finish_time = current_death_rate - current_death_progress * current_death_rate;

    return {
        case: {
            current: current_cases,
            progress: current_case_progress,
            rate: current_case_rate,
            finish_time: case_finish_time,
            confirmed_count: country.latest_confirmed_count
        },
        death: {
            current: current_deaths,
            progress: current_death_progress,
            rate: current_death_rate,
            finish_time: death_finish_time,
            confirmed_count: country.latest_death_count
        }
        // Will we need the following:
        // x,
        // t_zero,
        // current_date,
        // t_zero_array
    }
}

function build_bar(el, text_element, country, type) {
    const audio_file_name = type === 'case' ? 'confirmed' : 'death';

    const calculations = processCountryData(country);
    const { safe_name } = country
    const { current, rate, progress, finish_time, confirmed_count } = calculations[type];

    const value = Math.floor(current);
    
    updateCurrentRate(safe_name, rate, type);
    if (rate <= 0) {
      update_data_fields(safe_name, confirmed_count, Infinity, type);
    } else {
      update_data_fields(safe_name, current, rate, type); 
    }

    if (!Number.isFinite(rate) || rate <= 0) {
        text_element.innerText = confirmed_count;
        el.value = 0;
        return
    }

    el.value = progress * 100;
    text_element.innerText = value;

    start = new Date().getTime();

    shifty.tween({
        from: { x: progress },
        to: { x: 1 },
        duration: finish_time,
        step: (state) => {
            el.value = state.x;
        }
    }).then(state => {
        if (document.hasFocus())
            playAudio(audio_file_name);
        el.value = state.x;
        build_bar(el, text_element, country, type)
    });
};

function sort_elements(attribute, parent_element_id, filter, depth=0, multiplier = 1.0, discrete=false) {
    var parent_element = document.getElementById(parent_element_id);
    var children = parent_element.querySelectorAll(filter);
    var reordered = Array.from(children);
    if (discrete) {
        reordered.sort(function (a, b) {
            var val = 0;
            if (a.dataset[attribute] > b.dataset[attribute]) {
                val = -1;
            }
            if (b.dataset[attribute] > a.dataset[attribute]) {
                val = 1;
            }
            return val * multiplier;
        });
    } else {
        reordered.sort(function(a, b){
            return (multiplier * (parseFloat(a.dataset[attribute]) - parseFloat(b.dataset[attribute])));
        });
    }
    for(var child_index in reordered) {
        var currentNode = reordered[child_index];
        for (var i=0; i<depth; i++)
            currentNode = currentNode.parentNode;
        parent_element.appendChild(currentNode);    
    }
}

document.getElementById("sound-control").onclick = soundControlListener;

function soundControlListener() {
    soundEnabled = !soundEnabled;
    window.localStorage.setItem('soundEnabled', soundEnabled.toString());
    document.getElementById("sound-control").src = soundEnabled ? unmuteImage : muteImage;
}

document.getElementById("sort-selector").onchange = changeListener;

function changeListener(){
    var value = this.value;
    switch (value) {
        case 'caseCount':
        case 'deathCount':
            sort_elements(value, 'country-container', '.country-outer .country', depth=1, multiplier=-1.0);
            break;
        case 'caseRate':
        case 'deathRate':
            sort_elements(value, 'country-container', '.country-outer .country', depth=1, multiplier=1.0);
            break;
        case 'name':
        default:
            sort_elements('name', 'country-container', '.country-outer .country', depth=1, multiplier=-1.0, discrete=true);
    }
    
}

function mounted() {
    document.addEventListener('scroll', () => {
    var scrollPos = document.documentElement.scrollTop || document.body.scrollTop;
    });
    [].forEach.call(document.querySelectorAll('dialog'), (a) => {
        dialogPolyfill.registerDialog(a);
    });
}