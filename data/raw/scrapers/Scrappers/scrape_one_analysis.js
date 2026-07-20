(async () => {
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    console.log("%cStarting single-page extraction...", "color: cyan; font-weight: bold; font-size: 14px;");

    try {
        // 1) Click "اعرض الأشعار" (Show Poems)
        const showPoemsBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                  .find(btn => btn.innerText.includes("اعرض الأشعار"));
        if (showPoemsBtn) {
            showPoemsBtn.click();
            console.log("-> Clicked Show Poems.");
            await sleep(3000); 
        }

        // 2) Click "اعرض التعابير البلاغية" (Show Rhetoric/Analysis Table)
        const showRhetoricBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                         .find(btn => btn.innerText.includes("اعرض التعابير البلاغية"));
        if (showRhetoricBtn) {
            showRhetoricBtn.click();
            console.log("-> Clicked Show Rhetoric. Waiting for analysis...");
            await sleep(6000); // Analysis often takes time to generate the table
        }

        // 3) Uncheck checkboxes (to ensure full export if applicable)
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            if (cb.checked) cb.click();
        });
        console.log("-> Checkboxes cleared.");
        await sleep(1500);

        // 4) Click "Excel" to download
        const excelBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                              .find(btn => btn.innerText.trim().toUpperCase() === "EXCEL");
        
        if (excelBtn) {
            excelBtn.click();
            console.log("%c-> Excel download triggered!", "color: green; font-weight: bold;");
        } else {
            console.error("%c-> Excel button not found. Make sure the table has loaded.", "color: red;");
        }

    } catch (err) {
        console.error("Extraction failed:", err);
    }
})();