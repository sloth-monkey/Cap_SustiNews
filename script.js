// Configuration
const TOPICS = [
    "Carbon Accounting",
    "AI & Sustainability",
    "Climate Adaptation",
    "Climate Transition Plans",
    "SME Govt Support",
    "Enabling Corporate Action",
    "Sustainability Reporting",
    "Sustainability Financing"
];

const SOURCES = [
    "Financial Times",
    "The Economist",
    "The Edge",
    "Bloomberg",
    "Reuters",
    "Wall Street Journal",
    "The Guardian"
];

const SOURCE_CLASSES = {
    "Financial Times": "source-Financial",
    "The Economist": "source-TheEconomist",
    "The Edge": "source-TheEdge",
    "Bloomberg": "source-Bloomberg",
    "Reuters": "source-Reuters",
    "Wall Street Journal": "source-WSJ",
    "The Guardian": "source-Guardian"
};

const NEWS_DB = [];
let ACTIVE_TOPICS = new Set();
let CURRENT_DATE_IDX = 0; // 0 = today, 1 = yesterday, etc. (up to 6)

// Load Live Data
async function loadLiveData() {
    try {
        const response = await fetch('news_data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Populate the DB
        NEWS_DB.length = 0; // Clear existing
        data.forEach(dayArray => NEWS_DB.push(dayArray));
        
        // If the JSON didn't give us a full 7 days, pad the rest with empty arrays
        while (NEWS_DB.length < 7) {
            NEWS_DB.push([]);
        }
        
    } catch (error) {
        console.error("Failed to load news data:", error);
        alert("Failed to connect to the news server. Please check your data connection.");
        // Fallback to an empty 7-day structure to prevent the UI from completely breaking
        for(let i=0; i<7; i++) NEWS_DB.push([]);
    }
}

// Format Date Utility
function formatDateStr(dateObj, offset) {
    if (offset === 0) return "Today";
    if (offset === 1) return "Yesterday";
    return dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

// Render Filters
function renderFilters() {
    const filterContainer = document.getElementById("topic-filters");
    filterContainer.innerHTML = "";
    
    TOPICS.forEach(topic => {
        const btn = document.createElement("button");
        btn.className = `filter-pill ${ACTIVE_TOPICS.has(topic) ? "active" : ""}`;
        btn.dataset.topic = topic;
        btn.textContent = topic;
        
        btn.addEventListener("click", () => {
            if (ACTIVE_TOPICS.has(topic)) {
                ACTIVE_TOPICS.delete(topic);
            } else {
                ACTIVE_TOPICS.add(topic);
            }
            btn.classList.toggle("active");
            renderFeed();
        });
        
        filterContainer.appendChild(btn);
    });
}

// Render News Feed
function renderFeed() {
    const feedContainer = document.getElementById("news-feed");
    const currentArticles = NEWS_DB[CURRENT_DATE_IDX];
    
    // Filter by active topics
    let filtered = currentArticles;
    if (ACTIVE_TOPICS.size > 0) {
        filtered = currentArticles.filter(a => ACTIVE_TOPICS.has(a.topic));
    }
    
    if (filtered.length === 0) {
        feedContainer.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 4rem; text-align: center; color: var(--text-muted); font-family: var(--font-display); font-size: 1.2rem;">
                <i class="ph ph-empty" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                No articles match the selected topics for this day.
            </div>
        `;
        return;
    }
    
    feedContainer.innerHTML = filtered.map(article => `
        <article class="news-card">
            <div class="card-header">
                <span class="source-badge ${SOURCE_CLASSES[article.source]}">
                    ${getSourceIcon(article.source)} ${article.source}
                </span>
                <span class="article-time"><i class="ph ph-clock"></i> ${article.time}</span>
            </div>
            <h3 class="card-title"><a href="${article.url}" target="_blank">${article.title}</a></h3>
            <p class="card-snippet">${article.snippet}</p>
            <div class="card-footer">
                <span class="topic-tag">${article.topic}</span>
                <a href="${article.url}" target="_blank" class="read-more">Read Brief <i class="ph-bold ph-arrow-right"></i></a>
            </div>
        </article>
    `).join("");
}

function getSourceIcon(source) {
    if (source.includes("Financial") || source.includes("Street")) return '<i class="ph-fill ph-newspaper"></i>';
    if (source.includes("Economist") || source.includes("Guardian") || source.includes("Reuters")) return '<i class="ph-fill ph-book-open"></i>';
    if (source.includes("Bloomberg")) return '<i class="ph-fill ph-chart-line-up"></i>';
    return '<i class="ph-fill ph-globe-hemisphere-west"></i>'; // The Edge
}

// Setup Date Navigation
function setupArchiveNav() {
    const prevBtn = document.getElementById("prev-day");
    const nextBtn = document.getElementById("next-day");
    const displayStr = document.getElementById("current-date-display");
    const calendarBtn = document.getElementById("calendar-btn");
    const modal = document.getElementById("calendar-modal");
    const closeModal = document.getElementById("close-modal");
    const grid = document.getElementById("calendar-grid");
    
    const updateNavState = () => {
        // Update display text
        let dateObj = new Date();
        dateObj.setDate(dateObj.getDate() - CURRENT_DATE_IDX);
        displayStr.textContent = formatDateStr(dateObj, CURRENT_DATE_IDX);
        
        // Update buttons
        prevBtn.disabled = CURRENT_DATE_IDX >= 6; // Max 7 days history
        nextBtn.disabled = CURRENT_DATE_IDX <= 0; // Max today
        
        // Re-render feed
        renderFeed();
    };
    
    prevBtn.addEventListener("click", () => {
        if (CURRENT_DATE_IDX < 6) {
            CURRENT_DATE_IDX++;
            updateNavState();
        }
    });
    
    nextBtn.addEventListener("click", () => {
        if (CURRENT_DATE_IDX > 0) {
            CURRENT_DATE_IDX--;
            updateNavState();
        }
    });
    
    // Modal Setup
    calendarBtn.addEventListener("click", () => {
        // Build grid
        grid.innerHTML = "";
        for (let i = 0; i < 7; i++) {
            let offsetDate = new Date();
            offsetDate.setDate(offsetDate.getDate() - i);
            
            const btn = document.createElement("button");
            btn.className = `cal-day-btn ${i === CURRENT_DATE_IDX ? "active" : ""}`;
            
            const mainText = i === 0 ? "Today" : i === 1 ? "Yesterday" : offsetDate.toLocaleDateString('en-US', { weekday: 'long' });
            const subText = offsetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            btn.innerHTML = `<span>${mainText}</span> <span class="cal-subtext">${subText}</span>`;
            
            btn.addEventListener("click", () => {
                CURRENT_DATE_IDX = i;
                updateNavState();
                modal.classList.add("hidden");
            });
            grid.appendChild(btn);
        }
        modal.classList.remove("hidden");
    });
    
    closeModal.addEventListener("click", () => {
        modal.classList.add("hidden");
    });
    
    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.add("hidden");
    });
}

// Initialize App
document.addEventListener("DOMContentLoaded", async () => {
    await loadLiveData();
    renderFilters();
    renderFeed();
    setupArchiveNav();
});
