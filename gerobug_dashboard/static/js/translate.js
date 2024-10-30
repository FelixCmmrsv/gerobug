// Default language
let currentLanguage = 'en';

// Path to language JSON files
const languagePackPath = '/static/language_pack/';

// Function to load language JSON file and apply translations
async function loadLanguagePack(language) {
    try {
        const response = await fetch(`${languagePackPath}${language}.json`);
        if (response.ok) {
            const data = await response.json();
            applyTranslations(data);
        } else {
            console.error(`Failed to load language pack for ${language}`);
        }
    } catch (error) {
        console.error('Error loading language pack:', error);
    }
}

// Function to apply translations to the HTML content
function applyTranslations(data) {
    const page = document.body.getAttribute('data-page');
    const translations = data[page];

    if (translations) {
        Object.keys(translations).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = translations[id];
            }
        });
    }
}

// Function to change language and reload translations
function changeLanguage(lang) {
    if (lang !== currentLanguage) {
        currentLanguage = lang;
        loadLanguagePack(lang);
    }
}

// Load default language on page load
document.addEventListener('DOMContentLoaded', () => {
    loadLanguagePack(currentLanguage);
});
