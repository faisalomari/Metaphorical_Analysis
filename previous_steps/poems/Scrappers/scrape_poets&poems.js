async function startDeepAutomatedScraping() {
    const sleep = (ms) => new Promise(res => setTimeout(res, ms));
    const allPoetryVerses = []; 
    const analyzedPoets = new Set(); 

    const forceClick = (el) => {
        if (!el) return;
        ['mousedown', 'click', 'mouseup'].forEach(mouseEvent => {
            el.dispatchEvent(new MouseEvent(mouseEvent, {
                view: window, bubbles: true, cancelable: true, buttons: 1
            }));
        });
    };

    // 1. Get the list of all poets
    const arrow = document.querySelector('.ng-arrow-wrapper');
    forceClick(arrow);
    await sleep(2000);

    const options = Array.from(document.querySelectorAll('.ng-option'));
    const poetsToScrape = options.slice(1).map(opt => opt.innerText.trim());
    
    forceClick(arrow); 
    await sleep(2000);

    console.log(`Found ${poetsToScrape.length} poets. Starting Deep Scrape...`);

    for (let i = 0; i < poetsToScrape.length; i++) {
        const poetName = poetsToScrape[i];
        console.log(`--- Poet (${i + 1}/${poetsToScrape.length}): ${poetName} ---`);

        const currentArrow = document.querySelector('.ng-arrow-wrapper');
        forceClick(currentArrow);
        await sleep(2000);

        const targetOption = Array.from(document.querySelectorAll('.ng-option'))
            .find(opt => opt.innerText.trim() === poetName);

        if (targetOption) {
            forceClick(targetOption);
            await sleep(2500);

            const showBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                .find(btn => btn.innerText.includes('اعرض الأشعار'));
            
            if (showBtn) {
                forceClick(showBtn);
                await sleep(2500); 

                // 2. Filter Rows: Only those where the 3rd column is "نعم"
                const rows = document.querySelectorAll('tr.ff-book.ui-table-row');
                
                for (let row of rows) {
                    const cells = row.querySelectorAll('td');
                    // Check if the 3rd cell (index 2) contains "نعم"
                    const isAnalyzedText = cells[2]?.innerText.trim();
                    const analyzeBtn = row.querySelector('.analyze.pointer');

                    if (isAnalyzedText === "نعم" && analyzeBtn) {
                        const poemTitle = cells[1]?.innerText.trim();
                        console.log(`   Scraping Analyzed Poem: ${poemTitle}`);
                        analyzedPoets.add(poetName);

                        forceClick(analyzeBtn);
                        await sleep(2000); 

                        // 3. Scrape the Sadr and Ajuz
                        const verseRows = document.querySelectorAll('tr.poemCols');
                        verseRows.forEach(vRow => {
                            const sadr = vRow.querySelector('td:nth-child(3) label')?.innerText.trim() || "";
                            const ajuz = vRow.querySelector('td:nth-child(4) label')?.innerText.trim() || "";
                            
                            if (sadr || ajuz) {
                                allPoetryVerses.push({
                                    Poet: poetName,
                                    PoemTitle: poemTitle,
                                    Sadr: sadr,
                                    Ajuz: ajuz
                                });
                            }
                        });

                        // Close the analysis view/modal to reset for the next poem
                        const closeBtn = document.querySelector('.btn-close'); 
                        if (closeBtn) { 
                            forceClick(closeBtn); 
                            await sleep(2000); 
                        }
                    } else {
                        // Skip poems that say "لا"
                        continue; 
                    }
                }
            }
        }
        
        if (i % 5 === 0) console.log("Progress: Collected", allPoetryVerses.length, "verses so far.");
    }

    downloadResults(allPoetryVerses, Array.from(analyzedPoets));
}

function downloadResults(poetryData, poetList) {
    let csvContent = "\ufeffPoet,Poem Title,Sadr,Ajuz\n";
    poetryData.forEach(row => {
        csvContent += `"${row.Poet}","${row.PoemTitle}","${row.Sadr}","${row.Ajuz}"\n`;
    });

    let poetContent = poetList.join('\n');

    const triggerDownload = (content, fileName, type) => {
        const blob = new Blob([content], { type: type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.click();
    };

    triggerDownload(csvContent, 'Analyzed_Poetry_Master.csv', 'text/csv;charset=utf-8;');
    triggerDownload(poetContent, 'Analyzed_Poets_List.txt', 'text/plain;charset=utf-8;');
    
    console.log("Done! If no files downloaded, check if your browser blocked popups.");
}

startDeepAutomatedScraping();