/************************************************************
 *  FULL AUTOMATIC CHATGPT POETRY SENDER — VERSION C
 *  Sends EACH verse with ONE rhetorical element per message
 *  After finishing all elements for a verse → sends:
 *       "قم بجدول تلخيصي"
 ************************************************************/

const poem = [
    "لِمَنِ الدّيَارُ غَشِيتُهَا بِسُحَامِ    فَعَمَايَتَينِ فَهَضْبِ ذِي أقْدَامِ",
    "فَصَفَا الأطِيطِ فَصَاحَتَينِ فَعَاشِمٍ    تَمْشِي النّعَاجُ بِهِ مَعَ الآرَامِ",
    "دَارٌ لِهِرٍّ وَالرَّبَابِ وَفَرْتَنى    وَلَمِيسَ قَبْلَ حَوَادِثِ الأيّامِ",
    "عُوجَا عَلى الطَّلَلِ المُحِيلِ لَعَلَّنَا    نَبْكي الدّيارَ كما بكى ابنُ خِذامِ",
    "دَارٌ لَهُم إذْ هُمْ لأَهْلِكَ جِيرَةٌ    إذْ تَسْتَبِيكَ بِواضِحٍ بَسَّامِ",
    "أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا    كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ",
    "أَفَلا تَرَى أَظْعَانَهُنَّ بِعَاقِلٍ    كَالنَّخْلِ مِنْ شَوْكَانِ حِينِ صِرامِ",
    "حُورٌ يُعَلَّلْنَ العَبِيرَ رَوَادِعًا    كَمَهَا الشَّقَائِقِ أَوْ ظِبَاءِ سَلامِ",
    "وَظَلِلْتُ فِي دِمَنِ الدِّيَارِ كَأَنَّنِي    نَشْوَانُ بَاكَرَهُ صَبُوحُ مُدَامِ",
    "أنُفٌ كَلَوْنِ دَمِ الغَزَالِ مُعَتَّقٌ    مِنْ خَمْرِ عَانَةَ أَوْ كُرُومِ شِبَامِ",
    "وَكَأَنَّ شَارِبَهَا أَصَابَ لِسَانَهُ    مُومٌ يُخَالِطُ خَبْلَهُ بِعِظَامِ",
    "وَمُجِدَّةٍ أَعْمَلْتُهَا فَتَكَمَّشَتْ    رَتْكَ النَّعَامَةِ فِي طَرِيقٍ حَامِ",
    "يَأْتِي عَلَيْهَا القَوْمُ وَاهٍ خُفُّهَا    عَوْجَاءُ مَنْسِمُهَا رَثِيمٌ دَامِ",
    "جَالَتْ لِتَصْرَعَنِي فَقُلْتُ لَهَا اقْصِرِي    إِنِّي امْرُؤٌ صَرْعِي عَلَيْكِ حَرَامِ",
    "فَجُزِيتِ خَيْرَ جَزَاءِ نَاقَةِ وَاحِدٍ    وَرَجَعْتِ سَالِمَةَ القَرَا بِسَلامِ",
    "وَكَأَنَّمَا بَدْرٌ وَصِيلٌ كُتَيْفَةٍ    وَكَأَنَّمَا مِنْ عَاقِلٍ أَرْمَامُ",
    "أَبْلِغْ سُبَيْعًا إِنْ عَرَضْتَ رِسَالَةً    إِنِّي كَظَنِّكَ إِنْ عَشَوْتَ أَمَامِي",
    "أَقْصِرْ إِلَيْكَ مِنَ الوَعِيدِ فَإِنَّنِي    مِمَّا أُلاقِي لا أَشُدُّ حِزَامِي",
    "وَأُنَازِلُ البَطَلَ الكَمِيَّ نِزَالُهُ    وَإذَا أُناضِلُ لا تَطِيشُ سِهَامِي",
    "وَأنَا المُنَبِّهُ بَعْدَمَا قَدْ نَوَّمُوا    وَأنَا المُعَالِنُ صَفْحَةَ النُّوّامِ",
    "خالي ابنُ كَبشَةَ قد عَرَفْتَ مكانَهُ    وَأبُو يَزِيدَ وَرَهْطُهُ أعْمَامِي",
    "وَأنَا الّذِي عَلِمَتْ مَعَدٌّ فَضْلَهُ    وَنُشِدتُ عن حُجْرِ ابنِ أمِّ قَطَامِ",
    "وَإذَا أذِيتُ بِبَلْدَةٍ وَدّعْتُهَا    وَلا أُقِيمُ بِغَيرِ دَارِ مُقَامِ"
];

const rhetoricElements = [
    "استعارة", "تشبيه", "كناية", "مجاز", "تجريد", "مقابلة", "التهكم",
    "المشاكلة", "طباق", "المراجعة", "التفات", "مبالغة", "الرجوع",
    "الحذف", "جناس", "رد الأعجاز على الصدور", "التقسيم", "تورية",
    "مقابلة تضاد"
];

let verseIndex = 0;
let elementIndex = 0;
let summaryPending = false;


//----------------------------------------------
function writeMessage(text) {
    const editor = document.querySelector("#prompt-textarea");
    if (!editor) return alert("❌ Could not find editor.");
    editor.innerHTML = `<p>${text.replace(/\n/g, "<br>")}</p>`;
    editor.dispatchEvent(new Event("input", { bubbles: true }));
    editor.dispatchEvent(new Event("change", { bubbles: true }));
    editor.focus();
}


//----------------------------------------------
function waitForFinish(callback) {
    const observer = new MutationObserver(() => {
        const typing = document.querySelector("[data-testid='bot-typing']");
        if (!typing) {
            observer.disconnect();
            setTimeout(callback, 400);
        }
    });

    observer.observe(document.querySelector("main"), {
        childList: true,
        subtree: true
    });
}


//----------------------------------------------
// NEW FUNCTION WITH 5-SECOND DELAY BEFORE SEND
//----------------------------------------------
function safeClickSendWithDelay(callback) {
    const btn = document.querySelector("#composer-submit-button");
    const typing = document.querySelector("[data-testid='bot-typing']");
    const arrowPath = document.querySelector("svg path[d='M8.99992 16V6.41407L5.70696 9.70704C5.31643 10.0976 4.68342 10.0976 4.29289 9.70704C3.90237 9.31652 3.90237 8.6835 4.29289 8.29298L9.29289 3.29298L9.36907 3.22462C9.76184 2.90427 10.3408 2.92686 10.707 3.29298L15.707 8.29298L15.7753 8.36915C16.0957 8.76192 16.0731 9.34092 15.707 9.70704C15.3408 10.0732 14.7618 10.0958 14.3691 9.7754L14.2929 9.70704L10.9999 6.41407V16C10.9999 16.5523 10.5522 17 9.99992 17C9.44764 17 8.99992 16.5523 8.99992 16Z']");

    if (!btn || !arrowPath) {
        console.log("⏳ Waiting for send button...");
        setTimeout(() => safeClickSendWithDelay(callback), 1000);
        return;
    }

    if (typing) {
        console.log("⌛ Bot typing, wait...");
        setTimeout(() => safeClickSendWithDelay(callback), 1000);
        return;
    }

    // Everything ready → apply 5 second delay
    console.log("⏳ 5-second delay before sending...");
    setTimeout(() => {
        btn.click();
        waitForFinish(callback);
    }, 3000);
}


//----------------------------------------------
function run() {
    if (verseIndex >= poem.length) {
        console.log("✔️ Done with ALL verses");
        return;
    }

    if (summaryPending) {
        writeMessage("قم بجدول تلخيصي");
        summaryPending = false;
        safeClickSendWithDelay(run);
        return;
    }

    const verse = poem[verseIndex];

    if (elementIndex >= rhetoricElements.length) {
        summaryPending = true;
        elementIndex = 0;
        verseIndex++;
        run();
        return;
    }

    const element = rhetoricElements[elementIndex];
    const msg = `البيت: ${verse}  \n  العنصر البلاغي: ${element}`;

    console.log("➡️ Sending:", msg);

    writeMessage(msg);
    elementIndex++;

    safeClickSendWithDelay(run);
}


//----------------------------------------------
run();