/*******************************************************
 *  AUTOMATIC POETRY SENDER — YOUR UI VERSION
 *  - Uses ProseMirror #prompt-textarea  
 *  - Sends with #composer-submit-button  
 *  - Sends every FULL verse (صدر + عجز)  
 *  - 20 seconds delay between verses  
 *******************************************************/

window.stopScript = false;   // Set to true to stop anytime

// Full poetry — each item = ONE full بيت
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

let i = 0;

/************** WRITE INTO CHATGPT INPUT **************/
function writeMessage(text) {
    const editor = document.querySelector("#prompt-textarea");
    if (!editor) return alert("❌ Cannot find ChatGPT input field (#prompt-textarea).");

    editor.innerHTML = `<p>${text.replace(/\n/g, "<br>")}</p>`;
    editor.dispatchEvent(new Event("input", { bubbles: true }));
    editor.focus();
}

/************** CLICK SEND BUTTON **************/
function clickSend() {
    const btn = document.querySelector("#composer-submit-button");
    if (!btn) return alert("❌ Cannot find send button (#composer-submit-button).");
    btn.click();
}

/************** WAIT FOR CHATGPT TO FINISH **************/
function waitForFinish(callback) {
    const observer = new MutationObserver(() => {
        const typing = document.querySelector("[data-testid='bot-typing']");
        if (!typing) {
            observer.disconnect();
            setTimeout(callback, 500);
        }
    });
    observer.observe(document.querySelector("main"), {
        childList: true,
        subtree: true
    });
}

/************** MAIN LOOP **************/
function run() {
    if (window.stopScript) {
        console.log("⛔ Script stopped manually.");
        return;
    }

    if (i >= poem.length) {
        console.log("✔️ Finished sending the entire poem!");
        return;
    }

    const msg = `البيت رقم ${i + 1}:\n${poem[i]}`;
    console.log("➡️ Sending:", msg);

    writeMessage(msg);

    // WAIT 20 SECONDS BEFORE SENDING
    setTimeout(() => {
        clickSend();
        waitForFinish(run);
    }, 20000);  // 20-second delay

    i++;
}

/************** START **************/
run();
