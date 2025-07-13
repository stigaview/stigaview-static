// --- Configuration ---
const MEILISEARCH_HOST = "https://search.stigaview.com";
const MEILISEARCH_API_KEY = "c4f1ff671d18e2b16db7e0f203d7ac2e56673b097ebb81c5a4fa71fe174665fc";
const MEILISEARCH_INDEX_NAME = "controls";

const SEARCH_LIMIT = 10;

// --- DOM Elements ---
const openModalBtn = document.getElementById("open-search-modal-btn");
const modal = document.getElementById("search-modal");
const overlay = modal.querySelector(".modal-overlay");
const modalContent = modal.querySelector(".modal-content"); // Get content area
const closeModalBtn = modal.querySelector(".modal-close-btn");
const searchInput = document.getElementById("modal-search-input");
const resultsContainer = document.getElementById("modal-search-results");
const productSelect = document.getElementById("product-select");
const stigSelect = document.getElementById("stig-select");
const clearFiltersButton = document.getElementById("clear-filters");
const defaultPlaceholder =
    '<p class="results-placeholder">Start typing to see results.</p>';


async function loadProductStigMap() {
    try {
        const response = await fetch("/product-stig-map.json");
        return await response.json();
    } catch (error) {
        console.error("Failed to load product-STIG map:", error);
        return {};
    }
}

async function loadProductMap() {
    try {
        const response = await fetch("/products.json");
        return await response.json();
    } catch (error) {
        console.error("Failed to load product map:", error);
        return {};
    }
}


// --- State Management ---
let previouslyFocusedElement = null; // To store focus before modal opens
let productOptions = []; // Will hold all available products
let stigOptions = {};    // Will map products to their STIG versions
let selectedProduct = "";
let selectedStig = "";

function trapFocus(event) {
    if (!modal.classList.contains("active")) return; // Only trap if modal is active

    const focusableElements = modalContent.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement =
        focusableElements[focusableElements.length - 1];

    const isTabPressed = event.key === "Tab";

    if (!isTabPressed) {
        return;
    }

    if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstFocusableElement) {
            lastFocusableElement.focus();
            event.preventDefault();
        }
    } else {
        // Tab
        if (document.activeElement === lastFocusableElement) {
            firstFocusableElement.focus();
            event.preventDefault();
        }
    }
}

// --- Debounce Function ---
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Build filter string for Meilisearch
function buildFilterString() {
    const filterParts = [];

    if (selectedProduct) {
        filterParts.push(`product = "${selectedProduct}"`);
    }

    if (selectedStig) {
        filterParts.push(`stig = "${selectedStig}"`);
    }

    return filterParts.join(" AND ");
}


// --- Meilisearch Search Function ---
async function performSearch() {
    let query = searchInput.value.trim();
    if (!query) {
        resultsContainer.innerHTML = defaultPlaceholder;
        return;
    }

    resultsContainer.innerHTML = '<p class="results-loading">Loading...</p>';

    const searchUrl = `${MEILISEARCH_HOST}/indexes/${MEILISEARCH_INDEX_NAME}/search`;

    try {
        const response = await fetch(searchUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${MEILISEARCH_API_KEY}`,
            },
            body: JSON.stringify({
                q: query,
                limit: SEARCH_LIMIT,
                attributesToHighlight: ['title', 'description'],
                facets: ["product", "stig"],
                filter: buildFilterString(query),
            }),
        });

        if (!response.ok) {
            throw new Error(`Meilisearch error: ${response.statusText}`);
        }

        const data = await response.json();
        renderResults(data.hits);
    } catch (error) {
        console.error("Search failed:", error);
        resultsContainer.innerHTML = `<p class="results-error">Error fetching results. Please try again later.</p>`;
    }
}

// --- Render Search Results ---
function renderResults(hits) {
    if (!hits || hits.length === 0) {
        resultsContainer.innerHTML =
            '<p class="results-placeholder">No results found.</p>';
        return;
    }

    resultsContainer.innerHTML = ""; // Clear previous

    hits.forEach((hit) => {
        // --- Customize this part based on your index data structure ---
        const title = hit._formatted?.title || hit.title || "No Title";
        const description =
            hit._formatted?.description || hit.description || "";
        const url = hit.path || "#"; // Make sure links are focusable
        const stigVersion = hit.stig;
        const severity = hit.severity;
        const product = hit.product;

        const resultItem = document.createElement("div");
        resultItem.classList.add("result-item");

        // Ensure the link itself is rendered for focusability
        const link = document.createElement("a");
        link.href = url;
        link.innerHTML = `
            <h4>${title}</h4>
            <p>
                <span class="product-tag">${product}</span>
                <span class="version-tag">${stigVersion}</span>
                <span class="severity-tag severity-${severity}">${severity}</span>
           </p>
            ${description ? `<p>${description}</p>` : ""}
        `;

        resultItem.appendChild(link);
        // --- End of customization section ---

        resultsContainer.appendChild(resultItem);
    });
}

// --- Modal Open/Close Logic ---
function openModal() {
    previouslyFocusedElement = document.activeElement; // Store current focus
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
    // Use setTimeout to ensure modal is rendered before focusing
    setTimeout(() => {
        searchInput.focus(); // Focus the input field
    }, 50); // Small delay
    document.addEventListener("keydown", trapFocus); // Start trapping focus
}

function closeModal() {
    modal.classList.remove("active");
    document.body.style.overflow = "";
    searchInput.value = "";
    resultsContainer.innerHTML = defaultPlaceholder;
    document.removeEventListener("keydown", trapFocus); // Stop trapping focus
    if (previouslyFocusedElement) {
        previouslyFocusedElement.focus(); // Return focus to the original element
    }
}

// Update STIG dropdown options based on selected product
function updateStigDropdown() {
    // Clear current options (except the first "All Versions" option)
    while (stigSelect.options.length > 1) {
        stigSelect.remove(1);
    }

    // If no product selected, disable STIG dropdown
    if (!selectedProduct) {
        stigSelect.disabled = true;
        stigSelect.value = "";
        return;
    }

    // Get STIG versions for selected product
    const versions = stigOptions[selectedProduct] || [];

    // Add options for each version
    versions.forEach(version => {
        const option = document.createElement("option");
        option.value = version;
        option.textContent = version;
        stigSelect.appendChild(option);
    });

    // Enable the dropdown if there are versions available
    stigSelect.disabled = versions.length === 0;

    // Reset to "All Versions"
    stigSelect.value = "";
}

// Handle product dropdown change
function handleProductChange() {
    // Update selected product
    selectedProduct = productSelect.value;

    // Clear STIG selection if product changes
    selectedStig = "";

    // Update STIG dropdown based on selected product
    updateStigDropdown();

    // Perform new search with updated filters
    performSearch();
}

// Clear all selected filters
function clearAllFilters() {
    selectedProduct = "";
    selectedStig = "";

    productSelect.value = "";
    updateStigDropdown();

    performSearch();
}


// Handle STIG version dropdown change
function handleStigChange() {
    selectedStig = stigSelect.value;
    performSearch();
}



async function initializeDropdowns() {
    try {
        // Get all available products and their STIG versions
        const productStigPromise =  loadProductStigMap();
        const productPromise = loadProductMap();

        const [productMap, productStigMap] = await Promise.all(
            [productPromise, productStigPromise]
        )


        // Get all products
        productOptions = Object.keys(productStigMap).sort();

        // Store STIG options for each product
        stigOptions = productStigMap;

        // Populate product dropdown
        productOptions.forEach(product => {
            const option = document.createElement("option");
            option.value = product;
            option.textContent = productMap[product] || product;
            productSelect.appendChild(option);
        });

        // Sort product dropdown options (except the first "All Products" option)
        const firstOption = productSelect.options[0];
        const otherOptions = Array.from(productSelect.options).slice(1);
        otherOptions.sort((a, b) => a.value.localeCompare(b.value));

        productSelect.innerHTML = "";
        productSelect.appendChild(firstOption);
        otherOptions.forEach(option => productSelect.appendChild(option));
        firstOption.selected = true;

    } catch (error) {
        console.error("Failed to initialize dropdowns:", error);
    }
}


// --- Event Listeners ---
function setupEventListeners() {
    openModalBtn.addEventListener("click", openModal);
    closeModalBtn.addEventListener("click", closeModal);
    overlay.addEventListener("click", closeModal);
    productSelect.addEventListener("change", handleProductChange);
    stigSelect.addEventListener("change", handleStigChange);
    clearFiltersButton.addEventListener("click", clearAllFilters);


    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains("active")) {
            closeModal();
        }
    });

    const debouncedSearch = debounce(performSearch, 300);
    searchInput.addEventListener("input", (event) => {
        debouncedSearch();
    });
}

// --- Initial Setup ---

async function init() {
    await initializeDropdowns();
    setupEventListeners();
    modal.classList.remove("active");
    resultsContainer.innerHTML = defaultPlaceholder;
}

init();
