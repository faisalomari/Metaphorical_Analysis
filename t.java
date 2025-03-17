private ArrayList<wordInPoem> identificationTashbeehByLine(ArrayList<wordInPoem> firstPart , ArrayList<wordInPoem> secondPart){
    
    String[] startWithDemoyTokens = {"كأن", "فكأن", "وكأن","فكأن"};
    String[] startWithTokens = {"بمثل", "فمثل", "ومثل", "كال", "فكال", "وكال"};
    String[] allWordTokens = {"كما", "كأنما", "وكما", "فكما", "وكأنما", "فكأنما"};
    String[] verbTokens = { "حسب", "خال"};
    String[] verbTokens2 = {"شبه","ظن"};
    ArrayList<wordInPoem> identificationTashbeeh = new ArrayList<>();
    
    firstPart.addAll(secondPart);
    ArrayList<wordInPoem> allWordsInLine = firstPart;
    // Set<Map.Entry<Integer, String>> twoPartsInLine = allWordsInLine.entrySet();
   
    ArrayList<HashMap<String, String>> wordAnalysis1 = null;
    Integer indexWord = null;
    String word = null;
    
    for (wordInPoem entryWord: allWordsInLine) {
        indexWord = wordInPoem.getIndex();
        word = wordInPoem.getWord();
        wordAnalysis1 = null;
            
        try {
            wordAnalysis1 = WordAnalyzer.check_on(word);
        } catch (Exception ex) {
            wordAnalysis1 = null;
        }
            
        if(wordAnalysis1 == null){     
            try {
                wordAnalysis1 = WordAnalyzer.check_on(WordAnalyzer.remove_Diacritics(word));
            } catch (Exception ex) {
                wordAnalysis1 = null;

            }
        }
            
        Boolean  flag1=false;   
        if (wordAnalysis1 != null && !wordAnalysis1.isEmpty()) {
            for (HashMap<String, String> entry : wordAnalysis1) {
                System.out.println(entry.get("type")+"**************************************");
                if (WordAnalyzer.get_letters(word).contains("مثل") && entry.get("type").indexOf("فعل")!= -1) {
                    flag1=true;
                    System.out.println(entry.get("type"));
                }

            // find words start with tokens -------------------------------------------                       
            for (String demword : startWithTokens) {
                if (WordAnalyzer.remove_Diacritics(word).indexOf(demword) == 0 && !entry.get("prefix").equals("#")) {
                    
                    identificationTashbeeh.add(entryWord);
                    break;
                }
            }
            }
            if(flag1==true)
            {
                break;
            }else{
                if(WordAnalyzer.get_letters(word).contains("مثل") && !WordAnalyzer.get_letters(word).contains("مثلث") ){
                    identificationTashbeeh.add(entryWord;
                    break;
                }
            }

        }

        // find words start with Demoy tokens -------------------------------------------
        ArrayList<HashMap<String, String>> wordAnalysis = null;
        try {
            wordAnalysis = WordAnalyzer.check_on(word);
        } catch (Exception ex) {
            wordAnalysis = null;
        }
        Boolean  flag=false;   
        if (wordAnalysis != null && !wordAnalysis.isEmpty()) {
            for (String demword : startWithDemoyTokens) {
                System.out.println(demword);
                for (HashMap<String, String> entry : wordAnalysis) {
                    if ( (entry.get("type").indexOf("حرف ناسخ") != -1) || (entry.get("prefix").indexOf("حرف الجر") != -1 && entry.get("prefix").indexOf("ال:التعريف") != -1) ||
                            (entry.get("prefix").equals("كَ: حرف التشبيه") && entry.get("type").indexOf("فعل") == -1) ) {
                        if (WordAnalyzer.remove_Diacritics(word).indexOf(demword) == 0) {
                            identificationTashbeeh.add(entryWord);
                            flag=true;
                            break;
                        }
                    }
                }
                if(flag==true)
                    break;
            }
        }

        // find words, as is tokens -------------------------------------------
        for (String demword : allWordTokens) {

            if (WordAnalyzer.remove_Diacritics(word).equals(demword)) {
                identificationTashbeeh.add(entryWord);
                break;
            }
        }

        if (wordAnalysis != null && !wordAnalysis.isEmpty()) {
            for (HashMap<String, String> entry : wordAnalysis) {
                for (String demword : verbTokens) {
                    if (entry.get("type").indexOf("فعل ") != -1) {
                        String root = entry.get("root");
                        boolean isDemoy = false;
                        if (!demword.equals("خال")) {
                            if (demword.equals("حسب") && root.equals(demword)) {
                                isDemoy = true;
                            }

                            if (WordAnalyzer.remove_Diacritics(word).indexOf(demword) != -1 && root.equals(demword)) {
                                isDemoy = true;
                            }

                        } else {
                            if (WordAnalyzer.remove_Diacritics(word).indexOf(demword) != -1 && (root.equals("خلل") || root.equals("خيل"))) {
                                isDemoy = true;
                            }
                        }

                        if (isDemoy) {
                            identificationTashbeeh.add(entryWord);
                            break;

                        }
                    }
                }
            }
        }
            
            
        for (String demword : verbTokens2) {
            if (wordAnalysis != null && !wordAnalysis.isEmpty()) {
                for (HashMap<String, String> entry : wordAnalysis) {

                    if (entry.get("type").indexOf("فعل ") != -1) {
                        String root = entry.get("root");
                        boolean isDemoy = false;

                        if (WordAnalyzer.remove_Diacritics(word).indexOf(demword) != -1 && root.equals(demword)) {
                            isDemoy = true;
                        }

                        if (isDemoy) {
                            identificationTashbeeh.put(indexWord, word);
                            break;

                        }
                    }
                }
            }
        }
            
        if (word.length() > 1) {
            wordAnalysis = null;
            try {
                wordAnalysis = WordAnalyzer.check_on(word);
            } catch (Exception ex) {
                wordAnalysis = null;
            }
            boolean isval =true;
            String pre = "#";
            if (wordAnalysis != null && !wordAnalysis.isEmpty()) {
                for (HashMap<String, String> entry : wordAnalysis) {

                            if ((entry.get("prefix").equals("كَ: حرف التشبيه") || entry.get("prefix").equals("كَ: حرف الجر")) &&
                                    ((WordAnalyzer.remove_Diacritics(word).indexOf("كريم") == 0) ||
                                    (/*entry.get("type").indexOf("اسم")== -1 && */entry.get("postag").indexOf("مجرور") == -1) ) )  {
                                isval =false;

                            }
                            if((entry.get("prefix").equals("كَ: حرف التشبيه") || entry.get("prefix").equals("كَ: حرف الجر")))
                            {
                                 pre= entry.get("prefix");
                            }

                }

                if(isval && (pre.equals("كَ: حرف التشبيه") || pre.equals("كَ: حرف الجر"))){
                    identificationTashbeeh.add(entryWord);          
                }
            }
        }            
    }
    System.out.println();
    System.out.println("Demoy is done!");
    return identificationTashbeeh;
}

 מחלקת עזר-WordAnalyzer 
 using help class WordAnalyzer:
/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package TMProject;

import AlKhalil2.morphology.analyzer.AnalyzerTokens;
import java.util.ArrayList;
import java.util.HashMap;

/**
 *
 * @author ADMIN
 */
public class WordAnalyzer {

    static AnalyzerTokens analyzer = null;

    public static ArrayList<HashMap<String, String>> check_on(String textToBeAnalysed) throws Exception {
        ArrayList<HashMap<String, String>> analysis = new ArrayList<HashMap<String, String>>();

        if (analyzer == null) {
            analyzer = new AnalyzerTokens();
        }

        java.util.List result = analyzer.analyzerToken(textToBeAnalysed);
        AlKhalil2.util.constants.Static.allResults.put(textToBeAnalysed, result);
        java.util.List res = (java.util.List) AlKhalil2.util.constants.Static.allResults.get(textToBeAnalysed);

        if (result.isEmpty()) {

            analysis = null;

        } else {

            java.util.Iterator it = res.iterator();
            while (it.hasNext()) {
                AlKhalil2.morphology.result.model.Result rs = (AlKhalil2.morphology.result.model.Result) it.next();

                HashMap<String, String> entry = new HashMap<String, String>();
               // System.out.println(rs.getStem() +"-" +rs.getRoot()+"-" +rs.getType()+"-"+ rs.getPrefix());
               // System.out.println(rs.toString());
                entry.put("stem", remove_Diacritics(rs.getStem()));
                entry.put("root", rs.getRoot());
                entry.put("type", rs.getType());
                entry.put("prefix", rs.getPrefix());
                entry.put("lemmePattern", rs.getPatternLemma());
                entry.put("Suffix",rs.getSuffix());
                entry.put("status",rs.getDiacPatternStem());
                entry.put("1",rs.getLemma());
                entry.put("2",rs.getPatternStem());
                entry.put("postag",rs.getPostag());
                entry.put("4",rs.getPrefNoDec());
                entry.put("5",rs.getPriority());
                entry.put("6",rs.getVoweledWord());
                entry.put("7",rs.getSufNoDec());
                analysis.add(entry);

            }
        }
        return analysis;
    }

    public static String remove_Diacritics(String word) {
        String str = "";
        String ch;

        for (int i = 0; i < word.length(); i++) {
            ch = word.substring(i, i + 1);
            if (!ch.equals("ْ")
                    && !ch.equals("ّ")
                    && !ch.equals("ُ")
                    && !ch.equals("ٌ")
                    && !ch.equals("َ")
                    && !ch.equals("ً")
                    && !ch.equals("ِ")
                    && !ch.equals("ٍ")) {
                str += ch;
            }
        }
        return str;

    }

    public static String remove_last_diac(String word)
    {
        String ch=""+word.charAt(word.length()-1);
        
        if (!ch.equals("ْ")
                    && !ch.equals("ّ")
                    && !ch.equals("ُ")
                    && !ch.equals("ٌ")
                    && !ch.equals("َ")
                    && !ch.equals("ً")
                    && !ch.equals("ِ")
                    && !ch.equals("ٍ")) {
               return word.substring(0, word.length()-1);
            }
                   
        
        return word;
    }
    public static String get_letters(String word) {
        String str = "",space=" ",tmp;

        word=word.trim();
        
        for (int x = 0; x < word.length(); x++) {
            if (Character.isLetter(word.charAt(x))) {
                str += word.charAt(x);
            }else{ 
                tmp=""+word.charAt(x);
                if(space.equals(tmp))
                str +=" ";
            }
        }
        return str;

    }

}


