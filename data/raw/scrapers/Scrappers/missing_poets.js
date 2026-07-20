(async () => {
    // 1) Hardcoded list of all requested poets
    const poetsToProcess = [
            "المُرقِّشُ الأَصغر",
            "المُرَقِّشُ الأكبر (عمرو بن سعد بن مالك)",
            "ذو الرُّمّة",
            "قيس بن المُلَوَّح (مجنون ليلى)",
            "ابن قيس الرُّقيّات"
        ];

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    console.log(`%cStarting automation for ${poetsToProcess.length} poets...`, "color: yellow; font-weight: bold; font-size: 14px;");

    for (let i = 0; i < poetsToProcess.length; i++) {
        const poetName = poetsToProcess[i];
        console.log(`%c[${i + 1}/${poetsToProcess.length}] Processing: ${poetName}`, "color: cyan; font-weight: bold;");

        try {
            // 2) Open the list by clicking the arrow
            const arrowBtn = document.querySelector('.ng-arrow-wrapper');
            if (arrowBtn) {
                arrowBtn.click();
            } else {
                document.querySelector('ng-select').click();
            }
            await sleep(5000);

            // Find the option by text
            let options = Array.from(document.querySelectorAll('.ng-option'));
            let targetOption = options.find(opt => opt.innerText.trim() === poetName.trim());

            // If not found, try to use the search input (important for long lists)
            if (!targetOption) {
                const searchInput = document.querySelector('.ng-input input');
                if (searchInput) {
                    searchInput.value = poetName;
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    await sleep(5000);
                    options = Array.from(document.querySelectorAll('.ng-option'));
                    targetOption = options.find(opt => opt.innerText.includes(poetName));
                }
            }

            if (targetOption) {
                targetOption.click();
                console.log("-> Poet selected.");
            } else {
                console.error(`-> Could not find poet: ${poetName}`);
                continue;
            }
            await sleep(5000);

            // 3) Click "اعرض الأشعار"
            const showPoemsBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                      .find(btn => btn.innerText.includes("اعرض الأشعار"));
            if (showPoemsBtn) {
                showPoemsBtn.click();
                console.log("-> Clicked Show Poems.");
            }
            await sleep(5000); 

            // 4) Click "اعرض التعابير البلاغية"
            const showRhetoricBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                         .find(btn => btn.innerText.includes("اعرض التعابير البلاغية"));
            if (showRhetoricBtn) {
                showRhetoricBtn.click();
                console.log("-> Clicked Show Rhetoric.");
            }
            await sleep(5000); // Analysis takes longer

            // 5) Uncheck the checkboxes
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {
                if (cb.checked) cb.click();
            });
            console.log("-> Checkboxes cleared.");
            await sleep(5000);

            // 6) Click "Excel" to download
            const excelBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                  .find(btn => btn.innerText.trim().toUpperCase() === "EXCEL");
            if (excelBtn) {
                excelBtn.click();
                console.log(`%c-> Download started for ${poetName}`, "color: green;");
            } else {
                console.warn("-> Excel button not found for this poet.");
            }

            // Wait before moving to next poet to prevent browser overload
            await sleep(5000);

        } catch (err) {
            console.error(`Error processing ${poetName}:`, err);
        }
    }

    console.log("%c--- ALL POETS PROCESSED ---", "color: yellow; font-weight: bold; font-size: 16px;");
})();