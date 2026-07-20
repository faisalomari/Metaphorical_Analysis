(async () => {
    // 1) Hardcoded list of all requested poets
    const poetsToProcess = [
            "أبان بن عبد الحميد اللاحقي", "أبو تمّام", "أبو دلامة", "أبو ذؤيب الهذلي",
            "أبو فراس الحمداني", "أيمن بن خريم", "ابن قيس الرُّقيّات", "الأعشى ميمون",
            "الحكم بن عبدل", "الحمدوي", "الخنساء بنت عمرو بن الشريد", "السموأل بن عادياء",
            "الصنوبري", "الطرماح بن حكيم", "القرآن الكريم", "الكميت بن زيد الأسدي",
            "المتنبي", "المُرقِّشُ الأَصغر", "المُرَقِّشُ الأكبر (عمرو بن سعد بن مالك)",
            "النابغة الذبياني", "النجاشي الحارثي", "النمر بن تولب العكلي", "امرؤ القيس",
            "بشار بن برد", "تأبّطَ شَرًّا", "جرير بن عطيّة", "جميل بن معمر", "ديك الجن",
            "ذو الرُّمّة", "ربيعة بن مقروم", "طرفة بن العبد", "عبد الله بن عبد الحميد اللاحقي",
            "عبد الله بن عمر العرجي", "عبيد الله بن الحر", "عبيد بن الأخطل", "عفيف الدين التلمساني",
            "علقمة بن عبدة الفحل", "عمر بن أبي ربيعة", "عمران بن حطان", "قطري بن الفجاءة المازني",
            "قيس بن المُلَوَّح (مجنون ليلى)", "قيس بن ذريح", "مجهول (شعراء عباسيون منسيون)",
            "محمد بن هاشم (ابو بكر الخالدي)", "محمد بن يسير الرياشي", "مُليح بن الحكم",
            "يزيد بن مفرغ الحميري"
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
            await sleep(2000);

            // Find the option by text
            let options = Array.from(document.querySelectorAll('.ng-option'));
            let targetOption = options.find(opt => opt.innerText.trim() === poetName.trim());

            // If not found, try to use the search input (important for long lists)
            if (!targetOption) {
                const searchInput = document.querySelector('.ng-input input');
                if (searchInput) {
                    searchInput.value = poetName;
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    await sleep(2000);
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
            await sleep(2000);

            // 3) Click "اعرض الأشعار"
            const showPoemsBtn = Array.from(document.querySelectorAll('button.btn-rei'))
                                      .find(btn => btn.innerText.includes("اعرض الأشعار"));
            if (showPoemsBtn) {
                showPoemsBtn.click();
                console.log("-> Clicked Show Poems.");
            }
            await sleep(3000); 

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
            await sleep(2000);

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
            await sleep(4000);

        } catch (err) {
            console.error(`Error processing ${poetName}:`, err);
        }
    }

    console.log("%c--- ALL POETS PROCESSED ---", "color: yellow; font-weight: bold; font-size: 16px;");
})();