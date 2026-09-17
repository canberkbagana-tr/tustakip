import json
import re
import sys
from purify_module import purify_text

sys.stdout.reconfigure(encoding='utf-8')

# Detailed curated question data for Mart 2023
CURATED_DATA = {
    1: {
        "subject": "Anatomi",
        "topic": "Alt Ekstremite & Damarlar",
        "question": "Suprakondiler distal femur kırıklarında, femur arka komşuluğundaki aşağıdaki yapılardan hangisinin zedelenme riski en yüksektir?",
        "options": {
            "A": "Arteria femoralis",
            "B": "Arteria poplitea",
            "C": "Nervus ischiadicus",
            "D": "Nervus femoralis",
            "E": "Vena saphena parva"
        },
        "answer": "B",
        "explanation": "ARTERIA POPLITEA: Arteria femoralis'in canalis adductorius'un alt ucu olan hiatus adductorius'tan çıkınca fossa poplitea'daki devamıdır. Arteria poplitea, fossa poplitea'da yer alan yapıların en derinde olanıdır. Bu nedenle pulsasyonu en zor alınan arterdir. Yine derin seyrinden dolayı arteria poplitea, femurun distal kırıklarında ve diz ekleminin çıkıklarında en çok zarar gören yapıdır."
    },
    2: {
        "subject": "Anatomi",
        "topic": "Pelvis & Kas Anatomisi",
        "question": "Pelviste ramus inferior ossis pubis'in parçalı kırığının söz konusu olduğu bir travma sonrasında, aşağıdaki kaslardan hangisinin etkilenmesi en az olasıdır?",
        "options": {
            "A": "Musculus adductor brevis",
            "B": "Musculus gracilis",
            "C": "Musculus pectineus",
            "D": "Musculus adductor magnus",
            "E": "Musculus adductor minimus"
        },
        "answer": "C",
        "explanation": "Pubis'in ramus superior ossis pubis ve ramus inferior ossis pubis denilen iki kolu vardır. Ramus superior ossis pubis'e uyluğun medial bölge (addüktör) kaslarından musculus pectineus tutunur. Ramus inferior ossis pubis'e ise uyluğun diğer medial bölge (addüktör) kasları (musculus adductor magnus, musculus adductor minimus, musculus adductor longus, musculus adductor brevis ve musculus gracilis) tutunur."
    },
    3: {
        "subject": "Anatomi",
        "topic": "Perine & Pelvis Anatomisi",
        "question": "Musculus sphincter ani externus'un derin bölümünün lifleri aşağıdaki kaslardan hangisinin lifleri ile kaynaşmıştır?",
        "options": {
            "A": "Musculus iliococcygeus",
            "B": "Musculus coccygeus",
            "C": "Musculus puborectalis",
            "D": "Musculus pubovaginalis",
            "E": "Musculus bulbospongiosus"
        },
        "answer": "C",
        "explanation": "Musculus sphincter ani externus canalis analis'in alt parçasını kuşatan çizgili kastır. Pars profunda, pars superficialis ve pars subcutanea olmak üzere üç bölümden oluşur. Pars profunda; kemik tutunması yoktur, musculus levator ani'nin en medialdeki bölümü olan musculus puborectalis lifleri ile kaynaşır."
    },
    4: {
        "subject": "Anatomi",
        "topic": "Ayak Bileği Eklemi & Bağlar",
        "question": "Ayak bileğinin ani ve aşırı inversiyon hareketi sonucu burkulması sırasında aşağıdaki ligamentlerden hangisinin zedelenmesi en olasıdır?",
        "options": {
            "A": "Ligamentum talofibulare anterius",
            "B": "Ligamentum talofibulare posterius",
            "C": "Ligamentum calcaneonaviculare plantare",
            "D": "Ligamentum deltoideum (pars tibiotalaris anterior)",
            "E": "Ligamentum deltoideum (pars tibiotalaris posterior)"
        },
        "answer": "A",
        "explanation": "Articulatio talocruralis'te inversiyon yaralanmaları daha sık görülür. İnversiyon tipi ayak bileği burkulmalarında dış yan bağ olan ligamentum collaterale laterale gerilir. İnversiyon tipi burkulmada ilk ve en sık yaralanan ligament, ligamentum talofibulare anterius'tur."
    },
    6: {
        "subject": "Anatomi",
        "topic": "Nöroanatomi (Diencephalon)",
        "question": "Hypothalamus'a ait aşağıdaki komşuluk eşleştirmelerinden hangisi doğrudur?",
        "options": {
            "A": "Alt - Sulcus hypothalamicus",
            "B": "Üst - Sinus sphenoidalis",
            "C": "Alt - Sinus cavernosus",
            "D": "Lateral - Capsula interna",
            "E": "Medial - Ventriculus quartus"
        },
        "answer": "D",
        "explanation": "Hypothalamus komşulukları: Ön tarafta lamina terminalis ve commissura anterior; arka tarafta tegmentum mesencephali ve subthalamus; lateralde capsula interna; medialde üçüncü ventrikül (ventriculus tertius); yukarıda sulcus hypothalamicus; aşağıda üçüncü ventrikülün tabanı (chiasma opticum, tuber cinereum, infundibulum ve corpus mammillare) ile sınırlanır."
    },
    7: {
        "subject": "Anatomi",
        "topic": "Göz & Görme Yolları",
        "question": "Aşağıdakilerden hangisi hem pupilla ışık refleksinde hem de akomodasyon cevabında rol alır?",
        "options": {
            "A": "Ganglion ciliare",
            "B": "Nucleus pretectalis",
            "C": "Sulcus calcarinus",
            "D": "Corpus geniculatum laterale",
            "E": "Corpus geniculatum mediale"
        },
        "answer": "A",
        "explanation": "Pupilla ışık refleksinde afferent yol nervus opticus, efferent yol nervus oculomotorius'tur; pregangliyonik parasempatikler Edinger-Westphal çekirdeğinden çıkar ve ganglion ciliare'de sinaps yapar. Akomodasyon refleksinde de efferent yol yine Edinger-Westphal ve ganglion ciliare üzerinden musculus ciliaris ve musculus sphincter pupillae'ya gider. Dolayısıyla Ganglion ciliare her iki refleks yolunda da ortak ara istasyondur."
    },
    11: {
        "subject": "Anatomi",
        "topic": "Lenfatik Sistem",
        "question": "Glans penis'ten kaynaklandığı bilinen bir kanser olgusunun, aşağıdaki lenf düğümlerinden hangisi aracılığı ile metastaz yapması en olasıdır?",
        "options": {
            "A": "Nodi inguinales profundi",
            "B": "Nodi iliaci interni",
            "C": "Nodi inguinales superficiales",
            "D": "Nodi iliaci communes",
            "E": "Nodi lumbales"
        },
        "answer": "A",
        "explanation": "Nodi inguinales profundi (derin inguinal lenf düğümleri); vena femoralis'in medialinde yer alır. Bunlardan biri Cloquet/Rosenmüller lenf düğümüdür. Glans penis (veya clitoridis) ile labium minus pudendi'nin derin lenf damarları nodi inguinales profundi'ye drene olur."
    },
    12: {
        "subject": "Anatomi",
        "topic": "Periton & Pelvis Çıkmazları",
        "question": "Ayakta duran bir kadında periton sıvısının biriktiği en olası recessus aşağıdakilerden hangisidir?",
        "options": {
            "A": "Subhepaticus dexter",
            "B": "Subhepaticus sinister",
            "C": "Excavatio rectouterina (Douglas çıkmazı)",
            "D": "Excavatio vesicouterina",
            "E": "Excavatio rectovesicalis"
        },
        "answer": "C",
        "explanation": "Kadında periton rectum'dan uterus'a atlarken excavatio rectouterina'yı (Douglas çıkmazı) oluşturur. Excavatio rectouterina periton boşluğunun kadındaki en derin ve yerçekimiyle sıvının en çok toplandığı noktasıdır. Erkekteki karşılığı ise excavatio rectovesicalis'tir."
    },
    13: {
        "subject": "Anatomi",
        "topic": "Dil Kasları & İnnervasyon",
        "question": "Aşağıdaki kaslardan hangisi etkilendiğinde dil ucu öne doğru çıkartılamaz?",
        "options": {
            "A": "Musculus palatoglossus",
            "B": "Musculus genioglossus",
            "C": "Musculus hyoglossus",
            "D": "Musculus styloglossus",
            "E": "Musculus geniohyoideus"
        },
        "answer": "B",
        "explanation": "Musculus genioglossus dilin en büyük ekstrinsik kasıdır. Spina mentalis'ten başlar, iki taraflı çalıştığında dili öne ve dışarı doğru iter (protrüzyon yaptırır). Tek taraflı felcinde dil ucu lezyon tarafına sapar."
    },
    14: {
        "subject": "Anatomi",
        "topic": "Toraks & Mediasten",
        "question": "Üst gastrointestinal sistem endoskopisi esnasında kesici dişlerden yaklaşık 22-23 cm distalde (T4-T5 arası intervertebral disk seviyesi) özofagus lümeninin solda lateral yüzünden basıya uğradığı görülüyor. Aşağıdaki yapılardan hangisinin bu basıya neden olması en olasıdır?",
        "options": {
            "A": "Arteria subclavia sinistra",
            "B": "Arcus aortae",
            "C": "Arcus venae azygos",
            "D": "Atrium sinistrum",
            "E": "Hiatus oesophageus"
        },
        "answer": "B",
        "explanation": "Özofagus darlıkları ve mesafeleri: 1. Krikofaringeal darlık (15 cm), 2. Aortik darlık (Arcus aortae basısı, 22-23 cm, T4-T5 hizası soldan bası), 3. Bronşiyal darlık (Sol ana bronş basısı, 27 cm), 4. Diyafragmatik darlık (Hiatus oesophageus, 40 cm)."
    },
    16: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Bağ Dokusu & Adipoz Doku",
        "question": "Kahverengi yağ dokusuna ilişkin aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Hücrelerde yassılaşmamış yuvarlak çekirdek bulunur.",
            "B": "Hücre sitoplazmasında çok sayıda küçük yağ damlacığı bulunur (multiloküler).",
            "C": "Kemik iliğinde yerleşim gösterir.",
            "D": "Beyaz yağ dokusu hücrelerine göre daha küçük hücrelerden oluşur.",
            "E": "Hücrelerde mitokondri iç zarında termogenin (UCP-1) bulunur."
        },
        "answer": "C",
        "explanation": "Kahverengi yağ dokusu (multiloküler adipoz doku); bol mitokondri ve sitokrom içerir, mitokondri iç zarında termogenin (UCP-1) proteiniyle ATP sentezlemeden doğrudan ısı üretir (titremesiz termogenez). Yenidoğanda boyun, aksilla ve böbrek çevresinde bulunur; kemik iliğinde ise sarı/beyaz yağ dokusu yerleşim gösterir."
    },
    17: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Sinir Dokusu Histolojisi",
        "question": "Aşağıdakilerin hangisinde hücreyi çevreleyen eksternal lamina tabakası bulunur?",
        "options": {
            "A": "Langerhans hücresi",
            "B": "Plazma hücresi",
            "C": "Paneth hücresi",
            "D": "Mast hücresi",
            "E": "Schwann hücresi"
        },
        "answer": "E",
        "explanation": "Eksternal lamina (bazal lamina benzeri yapı); çizgili kas hücreleri, düz kas hücreleri, kardiyomiyositler ve periferik sinir sisteminde aksonları saran Schwann hücrelerinin etrafını kesintisiz bir tabaka şeklinde çevreler."
    },
    18: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Kardiyovasküler Embriyoloji",
        "question": "I. Atrial septal defekt (ASD)\nII. Ventriküler septal defekt (VSD)\nIII. Ektopia kordis\n\nYukarıdaki kalp anomalilerinden hangisi ya da hangileri endokardiyal yastık defektlerine bağlı olarak ortaya çıkar?",
        "options": {
            "A": "Yalnız I",
            "B": "Yalnız II",
            "C": "I ve II",
            "D": "II ve III",
            "E": "I, II ve III"
        },
        "answer": "C",
        "explanation": "Endokardiyal yastıklar (atriyoventriküler yastıkçıklar); atrial septumun alt kısmı (septum primum defekti / ostium primum tipi ASD), ventriküler septumun membranöz kısmı (VSD) ve AV kapakların (mitral/triküspit) gelişiminden sorumludur. Bu nedenle yastık defektlerinde ASD ve VSD görülür. Ektopia kordis ise sternum ve göğüs duvarının füzyon kusurudur."
    },
    19: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Genel Embriyoloji & Blastosist",
        "question": "Aşağıdakilerden hangisi fertilizasyon sonrasında ilk oluşan hücre gruplarındandır?",
        "options": {
            "A": "Trofoblast",
            "B": "Epiblast",
            "C": "Sinsityotrofoblast",
            "D": "Sitotrofoblast",
            "E": "Amniyoblast"
        },
        "answer": "A",
        "explanation": "Fertilizasyon sonrası morula blastosiste dönüştüğünde ilk kez iki belirgin hücre kitlesi ayrışır: İç hücre kitlesi (Embriyoblast) ve dış hücre tabakası (Trofoblast). Epiblast/hipoblast ise implantasyon esnasında bilaminer embriyo evresinde oluşur."
    },
    21: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Kardiyovasküler Histoloji",
        "question": "I. Subendokardiyum\nII. Subendotelyum\nIII. Subepikardiyum\n\nKoroner arterler yukarıdaki kalp tabakalarının hangilerinde yer alır?",
        "options": {
            "A": "Yalnız I",
            "B": "Yalnız II",
            "C": "Yalnız III",
            "D": "I ve II",
            "E": "I ve III"
        },
        "answer": "C",
        "explanation": "Kalp duvarı içten dışa endokard, miyokard ve epikarddan oluşur. Kalbi besleyen ana koroner arterler ve büyük dalları kalbin dış yüzeyinde epikardın altındaki subepikardiyal yağ dokusu içerisinde seyreder ve buradan miyokarda doğru dallar verir."
    },
    22: {
        "subject": "Histoloji ve Embriyoloji",
        "topic": "Lenfoid Organlar & İmmün Sistem",
        "question": "Aşağıdaki lenfoid organların hangisinde lenf folikülü bulunmaz?",
        "options": {
            "A": "Dalak",
            "B": "Tonsilla palatina",
            "C": "Timus",
            "D": "Mukoza ile ilişkili lenfoid doku (MALT)",
            "E": "Lenf düğümü"
        },
        "answer": "C",
        "explanation": "Timüs primer lenfoid bir organdır ve T lenfositlerin matürasyon merkezidir; yapısında B lenfositlerin germinal merkezli lenfoid folikülleri (nodülleri) bulunmaz. Dalak beyaz pulpası, tonsilla palatina, lenf nodu korteksi ve MALT (Peyer plakları) ise zengin lenfoid foliküller içerir."
    },
    23: {
        "subject": "Fizyoloji",
        "topic": "Hücre Zarı & Geçit Bağlantıları",
        "question": "Hücreler arasında bağlantı sağlayan geçit bağlantıları (gap junction / neksus) ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Sadece moleküler boyut esaslı seçicilik gösteren protein kanallarıdır.",
            "B": "Kalpte geçit bağlantı sayısı fazla ise elektriksel uyarı iletimi hızlıdır.",
            "C": "Geçit bağlantıları hücrede daha az enerji harcanmasını sağlar.",
            "D": "Geçit bağlantıları iskelet kası ve eritrositlerde bulunmaz.",
            "E": "Kalsiyum düzeyinin azalması ve artmış hücre içi pH geçit bağlantıları kapatır."
        },
        "answer": "E",
        "explanation": "Geçit bağlantıları (gap junction, neksus); 6 konneksin proteininin oluşturduğu konneksonlardan meydana gelir. Kalsiyum iyonunun ARTMASI ve intraselüler asidoz (DÜŞÜK pH) konneksonları kapatır. İskelet kası ve eritrositlerde gap junction bulunmaz."
    },
    25: {
        "subject": "Fizyoloji",
        "topic": "Hemostaz & Koagülasyon",
        "question": "Aşağıdaki durumlardan hangisi plazmadaki Protein C'yi aktif hale getirir?",
        "options": {
            "A": "Trombinin trombomoduline bağlanması",
            "B": "Antitrombin III aktivasyonu",
            "C": "Doku plazminojen aktivatörü artışı",
            "D": "Fibrinojenin fibrin monomerlerine dönüşmesi",
            "E": "Faktör VIIIa inaktivasyonu"
        },
        "answer": "A",
        "explanation": "Endotel hücresi yüzeyindeki trombomoduline bağlanan trombin, prokoagülan özelliğini kaybeder ve Protein C'yi aktifleştirir. Aktif Protein C (APC), kofaktörü Protein S ile birlikte kofaktör Faktör Va ve Faktör VIIIa'yı proteolitik olarak inaktive ederek güçlü antikoagülan etki oluşturur."
    },
    27: {
        "subject": "Fizyoloji",
        "topic": "Endokrinoloji & Hormon Yapıları",
        "question": "Aşağıdakilerden hangisi peptit yapıda bir hormonun özelliğidir?",
        "options": {
            "A": "Hedef hücre çekirdeğinde reseptöre bağlanma",
            "B": "Plazmada taşıyıcı proteine yüksek oranda bağlanarak taşınma",
            "C": "Yarı ömrünün steroid hormonlara göre çok uzun olması",
            "D": "Sitoplazmada membranöz salgı veziküllerinde depolanma",
            "E": "Kolesterolden de novo sentezlenme"
        },
        "answer": "D",
        "explanation": "Peptit ve protein hormonlar granüllü endoplazmik retikulumda preprohormon olarak sentezlenir, Golgi'de veziküller içine paketlenir ve ekzositoz uyarısı gelene kadar sitoplazmada depolanır. Suda çözündükleri için plazmada serbest taşınırlar ve hücre zarı yüzey reseptörlerine bağlanırlar."
    },
    28: {
        "subject": "Fizyoloji",
        "topic": "Nörofizyoloji & Glia Hücreleri",
        "question": "Merkezi sinir sisteminde ekstraselüler ortamdaki glutamatı alarak olası eksitotoksisiteyi önleyen gliya hücresi aşağıdakilerden hangisidir?",
        "options": {
            "A": "Mikroglia",
            "B": "Ependim hücresi",
            "C": "Oligodendrosit",
            "D": "Astrosit",
            "E": "Schwann hücresi"
        },
        "answer": "D",
        "explanation": "Astrositler sinaptik aralıktaki ekstraselüler K+ fazlalığını tamponlar ve salınan glutamatı EAAT (eksitatör aminoasit taşıyıcı) ile hücre içine alıp glutamin sentetaz ile glutamine çevirerek nöronu eksitotoksisiteden korur."
    },
    30: {
        "subject": "Fizyoloji",
        "topic": "Solunum & Yüksek İrtifa Adaptasyonu",
        "question": "Deniz seviyesinde yaşayan 28 yaşındaki bir kadının, kısa sürede 3.000 metre yüksekliğe tırmanması durumunda meydana gelecek akut uyum yanıtlarından biri değildir?",
        "options": {
            "A": "Aortik ark ve karotik bifurkasyondaki periferik kemoreseptörler hipoksi ile uyarılır.",
            "B": "Arteriyel hipokapni meydana gelir.",
            "C": "Solunumsal alkaloz meydana gelir.",
            "D": "Kandaki karbondioksit santral kemoreseptörleri ve solunum merkezini uyarır.",
            "E": "Dakika ventilasyon hacmi artar."
        },
        "answer": "D",
        "explanation": "Yüksek irtifada barometrik basınç düşer ve hipoksi periferik kemoreseptörleri uyararak hiperventilasyona yol açar. Hiperventilasyon ile CO2 atılır, PaCO2 düşer (hipokapni) ve respiratuar alkaloz gelişir. Bu nedenle kandaki CO2 santral kemoreseptörleri uyarmaz, aksine düşük CO2 santral solunum dürtüsünü baskılar."
    },
    31: {
        "subject": "Fizyoloji",
        "topic": "Solunum & Kemoreseptör Mekanizması",
        "question": "Karotid ve aortik cisimciklerde bulunan glomus hücrelerinin hipoksiye karşı oluşturduğu yanıtta aşağıdakilerden hangisi gözlenir?",
        "options": {
            "A": "Na-H değiştiricisinin aktivasyonu",
            "B": "K+ kanallarının inaktivasyonu (kapanması)",
            "C": "Na+ kanallarının aktivasyonu",
            "D": "Ca+2 kanallarının inaktivasyonu",
            "E": "Cl- kanallarının aktivasyonu"
        },
        "answer": "B",
        "explanation": "Glomus Tip 1 hücrelerinde hipoksi (PaO2 düşüşü), O2'ye duyarlı K+ kanallarını inaktive eder (kapatır). Hücreden K+ çıkışı azaldığı için hücre depolarize olur. Depolarizasyon voltaj kapılı L-tipi Ca+2 kanallarını açar, hücre içine Ca+2 girişi veziküllerden nörotransmitter (dopamin, asetilkolin) ekzositozunu tetikler ve afferent sinir uyarılır."
    },
    32: {
        "subject": "Fizyoloji",
        "topic": "Dolaşım & Şok Fizyolojisi",
        "question": "Kanama nedeniyle dekompanse olmayan şok tablosuyla acil servise getirilen 25 yaşındaki erkek hastada aşağıdaki bulgulardan hangisi gözlenmez?",
        "options": {
            "A": "Deride vazokonstrüksiyon ve solukluk",
            "B": "Antidiüretik hormon (ADH) düzeyinde azalma",
            "C": "Taşikardi",
            "D": "Renin salgısında artma",
            "E": "Plazma glukokortikoid düzeyinde artma"
        },
        "answer": "B",
        "explanation": "Akut kan kaybı ve hipovolemi durumunda vücut kan basıncını korumak için sempatik sistemi, Renin-Anjiyotensin-Aldosteron sistemini ve hipotalamustan ADH (vazopressin) salınımını belirgin şekilde ARTIRIR. ADH düzeyinde azalma değil, belirgin artış gözlenir."
    },
    33: {
        "subject": "Biyokimya",
        "topic": "Metabolizma & Mekik Sistemleri",
        "question": "Sitoplazmada NADH'da toplanan elektronları mitokondriye taşıyan mitokondriyal malat-aspartat mekiği ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Malat, aspartat ve oksaloasetat mitokondri membranını doğrudan geçen moleküllerdir.",
            "B": "Sitozolik aspartat transaminaz enziminin etkisiyle oksaloasetat ve L-glutamat oluşur.",
            "C": "Bu mekikte 2 membran taşıyıcısı ve 4 enzim rol alır.",
            "D": "Mitokondriyal malat dehidrogenaz L-malattan oksaloasetat oluşumunu katalize eder.",
            "E": "Oksaloasetatın transaminasyonu için L-glutamata ihtiyaç vardır."
        },
        "answer": "A",
        "explanation": "Oksaloasetatın mitokondri iç zarında taşıyıcısı YOKTUR, bu nedenle iç zarı doğrudan geçemez. Malata indirgenerek veya aspartata transamine edilerek zardan geçirilir."
    },
    36: {
        "subject": "Biyokimya",
        "topic": "Protein Kimyası & İzoelektrik Nokta",
        "question": "Bir proteini kodlayan DNA dizisindeki nokta mutasyonları sonucunda amino asit dizisinde oluşan;\nI. Lösin → Fenilalanin\nII. Alanin → Glutamat\nIII. İzolösin → Lizin\n\nYukarıdaki mutasyonlardan hangileri bu proteinin izoelektrik noktasında (pI) değişikliğe neden olur?",
        "options": {
            "A": "Yalnız I",
            "B": "Yalnız II",
            "C": "I ve III",
            "D": "II ve III",
            "E": "I, II ve III"
        },
        "answer": "D",
        "explanation": "Bir proteinin izoelektrik noktasının (pI) değişmesi için net yükünün değişmesi gerekir. Lösin ve Fenilalanin her ikisi de yüksüz apolar amino asitlerdir (net yük değişmez). Alanin (yüksüz) yerine Glutamat (-1 negatif) veya İzolösin (yüksüz) yerine Lizin (+1 pozitif) gelmesi proteinin net yükünü ve izoelektrik noktasını değiştirir."
    },
    38: {
        "subject": "Biyokimya",
        "topic": "Doğuştan Metabolik Hastalıklar",
        "question": "Yenidoğan döneminde beslenme güçlüğü, kusma ve letarji şikayetleriyle getirilen hastada serum amonyak düzeyi 650 µmol/L (N: 0-100), idrarda keton (++) ve anyon gap artışlı metabolik asidoz saptanıyor. Plazma C3-açilkarnitin (propiyonilkarnitin) düzeyi artmış olan hastada aşağıdaki metabolitlerden hangisinin idrarda artışı ayırıcı tanı için yol göstericidir?",
        "options": {
            "A": "3-OH-dikarboksilik asit",
            "B": "2-ketoglutarik asit",
            "C": "Metilmalonik asit",
            "D": "3-metil-krotonilglisin",
            "E": "3-OH-izobütirik asit"
        },
        "answer": "C",
        "explanation": "C3-açilkarnitin artışı Propiyonik asidemi ve Metilmalonik asidemi için ortaktır. Bu iki hastalığın kesin ayrımında idrarda metilmalonik asit düzeyine bakılır; metilmalonik asit artmışsa Metilmalonik asidemi, normal ise Propiyonik asidemi tanısı konur."
    },
    39: {
        "subject": "Biyokimya",
        "topic": "Vitaminler & Koenzimler",
        "question": "I. Homosistein metiltransferaz\nII. Metionin sentaz\nIII. Sistatiyonin beta-sentaz\nIV. Sistatiyoninaz\n\nPiridoksal fosfat (Vitamin B6) eksikliğinde, yukarıdaki metionin metabolizması enzimlerinden hangilerinin aktivitesinde azalma görülür?",
        "options": {
            "A": "I ve III",
            "B": "I ve IV",
            "C": "II ve III",
            "D": "III ve IV",
            "E": "I, II ve IV"
        },
        "answer": "D",
        "explanation": "Metionin transsülfürasyon yolunda homosisteinden sistein sentezlenirken görev alan Sistatiyonin beta-sentaz ve Sistatiyoninaz (sistatiyonin gamma-liyaz) enzimleri piridoksal fosfatı (Vitamin B6) koenzim olarak kullanır."
    },
    40: {
        "subject": "Biyokimya",
        "topic": "Üre Döngüsü & Hiperamonyemi",
        "question": "On bir yaşındaki çocuk hasta bilinç bulanıklığı, bulantı ve kusma şikayetleri ile acil servise getiriliyor. Karaciğer ve böbrek testleri normal, plazma amonyak düzeyi 280 µmol/L bulunuyor. İleri tetkikte ornitin transkarbamoilaz (OTC) enzim eksikliği saptanan hastada aşağıdakilerden hangisinde artış beklenir?",
        "options": {
            "A": "Serotonin",
            "B": "Glutamin",
            "C": "Dopamin",
            "D": "Arginin",
            "E": "GABA"
        },
        "answer": "B",
        "explanation": "Üre siklus defektlerinde kanda amonyak birikir. Serbest amonyak beyinde astrositler tarafından alfa-ketoglutarat ve glutamata bağlanarak GLUTAMİN'e dönüştürülür. Plazma ve beyin glutamin düzeyleri belirgin şekilde artar; bu durum astrosit şişmesine ve serebral ödeme neden olur."
    },
    41: {
        "subject": "Biyokimya",
        "topic": "Amino Asit & Tek Karbon Metabolizması",
        "question": "Aşağıdaki amino asitlerden hangisi ATP'den adenozil grubu alarak fosfor içermeyen yüksek enerjili bileşik oluşturur?",
        "options": {
            "A": "Alanin",
            "B": "Tirozin",
            "C": "Sistein",
            "D": "Metionin",
            "E": "Histidin"
        },
        "answer": "D",
        "explanation": "Metionin, metionin adenoziltransferaz enzimiyle ATP'nin tüm fosfatlarını bırakıp adenozil grubunu almasıyla S-adenozilmetionin (SAM) oluşturur. SAM fosfat içermeyen, yüksek enerjili sülfonyum bağı içeren evrensel metil donörüdür."
    },
    42: {
        "subject": "Biyokimya",
        "topic": "Hemoglobin & Gaz Taşınması",
        "question": "Burnuna yabancı cisim kaçan çocukta akut parsiyel solunum yolu obstrüksiyonu gelişiyor. Bu hastada tıbbi müdahale öncesi hemoglobin-oksijen affinitesi ile ilgili aşağıdaki ifadelerden hangisi doğrudur?",
        "options": {
            "A": "pCO2 artışına bağlı oksijen satürasyon eğrisi sağa kaymıştır.",
            "B": "pH artışına bağlı oksijen satürasyon eğrisi sağa kaymıştır.",
            "C": "pH düşüklüğüne bağlı R (oksi) formu baskındır.",
            "D": "pO2 azlığına bağlı oksijen satürasyon eğrisi sola kaymıştır.",
            "E": "Oksijen satürasyon eğrisinde bir değişiklik olmamıştır."
        },
        "answer": "A",
        "explanation": "Akut hava yolu tıkanıklığı CO2 birikimine (hiperkapni) ve respiratuar asidoza (H+ artışı) yol açar. Bohr etkisine göre artmış H+ ve artmış pCO2 hemoglobinin deoksi (T) formunu stabilize ederek oksijen satürasyon eğrisini SAĞA kaydırır."
    },
    43: {
        "subject": "Biyokimya",
        "topic": "Lipid Biyosentezi",
        "question": "Aşağıdakilerden hangisi hem triaçilgliserol (TAG) hem de kardiyolipin biyosentezinde ortak ara ürün olarak rol alır?",
        "options": {
            "A": "Sfinganin",
            "B": "Fosfatidik asit",
            "C": "Fosfatidilgliserol 3-fosfat",
            "D": "CDP-diaçilgliserol",
            "E": "Fosfatidilserin"
        },
        "answer": "B",
        "explanation": "Gliserol 3-fosfatın iki kez açillenmesiyle oluşan Fosfatidik asit (1,2-diaçilgliserol fosfat), hem triaçilgliserollerin hem de gliserofosfolipidlerin (kardiyolipin, fosfatidilkolin, fosfatidiletanolamin vb.) biyosentezindeki ortak merkez moleküldür."
    },
    45: {
        "subject": "Biyokimya",
        "topic": "Lipoliz & Adipoz Sinyal İletimi",
        "question": "Yağ dokusunda, lipid damlacıklarının etrafını saran ve hormona duyarlı lipaz ile etkileşen protein aşağıdakilerden hangisidir?",
        "options": {
            "A": "Protein kinaz A",
            "B": "Apo C-II",
            "C": "Perilipin",
            "D": "G proteini",
            "E": "Termogenin"
        },
        "answer": "C",
        "explanation": "Perilipin adipoz dokuda intraselüler lipid damlacıklarının yüzeyini örterek bazal durumda trigliseridleri hormona duyarlı lipazın (HSL) hidrolizinden korur. Glukagon veya epinefrin ile PKA uyarılınca perilipin fosforillenir ve HSL damlacık yüzeyine erişip lipolizi başlatır."
    },
    50: {
        "subject": "Biyokimya",
        "topic": "Kanser Biyokimyası & Onkogenler",
        "question": "Aşağıdaki kolorektal karsinogenez ile ilişkili genler ve görevleri eşleştirmelerinden hangisi yanlıştır?",
        "options": {
            "A": "K-ras - Tirozin kinaz sinyal iletiminde rol alır.",
            "B": "Beta-katenin - Epitel dokuların integrasyonunu sağlar.",
            "C": "APC - WNT sinyal iletimini antagonize eder.",
            "D": "CDC4 - Ubikitin bağımlı proteolizde görevlidir.",
            "E": "BAX - Apopitozu inhibe eder."
        },
        "answer": "E",
        "explanation": "BAX pro-apoptotik bir proteindir; mitokondri dış zarında gözenek açarak sitokrom c salınımını ve apopitozu uyarır (apopitozu indükler). Apopitozu inhibe eden protein BCL-2'dir."
    },
    51: {
        "subject": "Biyokimya",
        "topic": "Toksikoloji & Ksenobiyotik Metabolizması",
        "question": "Yüksek doz parasetamol alma öyküsü ile getirilen ve antidot tedavisi başlanan hastaya uygulanan N-asetilsisteinin aşağıdaki metabolitlerden hangisinin seviyesini artırması beklenir?",
        "options": {
            "A": "Glutatyon",
            "B": "N-asetil-p-benzokinon imin (NAPQI)",
            "C": "Benzoat",
            "D": "Hippürik asit",
            "E": "Dimerkaprol"
        },
        "answer": "A",
        "explanation": "Parasetamol toksik dozda CYP2E1 ile reaktif hepatotoksik NAPQI'ye dönüşür. NAPQI karaciğer glutatyon depolarını tüketir. Antidot olarak verilen N-asetilsistein (NAC), sistein sağlayarak intraselüler GLUTATYON sentezini artırır ve NAPQI'yi nötralize eder."
    },
    52: {
        "subject": "Biyokimya",
        "topic": "Serbest Radikaller & Oksidatif Stres",
        "question": "Hücresel makromoleküller için diğerlerine göre en reaktif ve en toksik olan reaktif oksijen türü (ROS) aşağıdakilerden hangisidir?",
        "options": {
            "A": "Süperoksit radikali",
            "B": "Hidroksil radikali (OH*)",
            "C": "Hidrojen peroksit",
            "D": "Singlet oksijen",
            "E": "Lipid peroksit radikali"
        },
        "answer": "B",
        "explanation": "Hidroksil radikali (OH*); Fenton ve Haber-Weiss reaksiyonları ile oluşur. Yarı ömrü nanosaniyeler mertebesinde olup karşılaştığı DNA, protein ve lipid gibi tüm biyolojik moleküllere anında zarar veren en reaktif ve en sitotoksik oksijen radikalidir."
    },
    55: {
        "subject": "Mikrobiyoloji",
        "topic": "Klinik Mikrobiyoloji & Kan Kültürü",
        "question": "Kan kültürlerinin laboratuvara gönderilme süresi ve transport sıcaklığı ile ilgili aşağıdaki eşleştirmelerden hangisi doğrudur?",
        "options": {
            "A": "<2 saat; 37 °C",
            "B": "<2 saat; 25 °C (oda ısısı)",
            "C": "<30 dakika; 4 °C",
            "D": "<2 saat; 4 °C",
            "E": "<30 dakika; 37 °C"
        },
        "answer": "B",
        "explanation": "Kan kültür şişeleri kan alındıktan sonra asla buzdolabına (4 °C) konulmamalıdır; en geç 2 saat içerisinde oda sıcaklığında (yaklaşık 25 °C) laboratuvara ulaştırılmalıdır."
    },
    56: {
        "subject": "Mikrobiyoloji",
        "topic": "Sterilizasyon & Dezenfeksiyon",
        "question": "Yarı kritik tıbbi cihazlara uygulanacak dekontaminasyon işlemi için tercih edilmesi en uygun yüksek düzey dezenfektan aşağıdakilerden hangisidir?",
        "options": {
            "A": "Aldehitler (Glutaraldehit)",
            "B": "İyodoforlar",
            "C": "Kuaterner amonyum bileşikleri",
            "D": "Alkoller",
            "E": "Fenoller"
        },
        "answer": "A",
        "explanation": "Mukoza veya bütünlüğü bozulmuş cilde temas eden yarı kritik cihazlar (fleksibl endoskoplar vb.) için yüksek düzey dezenfektanlar (glutaraldehit, ortofitalaldehit, perasetik asit, hidrojen peroksit) kullanılır. İyodofor, alkol ve kuaterner amonyum orta/düşük düzey dezenfektandır."
    },
    57: {
        "subject": "Mikrobiyoloji",
        "topic": "Bakteriyoloji & Biyokimyasal Testler",
        "question": "Gram-negatif bakterilerin tanımlanmasında kullanılan, glukoz metabolizması sonucunda asetoin ve 2,3-butandiol oluşumunu gösteren test aşağıdakilerden hangisidir?",
        "options": {
            "A": "Metil kırmızısı testi",
            "B": "İndol testi",
            "C": "PYR testi",
            "D": "ONPG testi",
            "E": "Voges-Proskauer testi"
        },
        "answer": "E",
        "explanation": "IMViC testlerinden Voges-Proskauer (VP) testi, bakterinin glukozu bütandiol fermantasyon yoluyla yıkarak nötr son ürün olan asetoin (asetilmetilkarbinol) üretip üretmediğini saptar. Metil kırmızısı (MR) ise karışık asit fermantasyonunu gösterir."
    },
    68: {
        "subject": "Mikrobiyoloji",
        "topic": "Viroloji & DNA Virüsleri",
        "question": "Beşinci hastalık etkeni olan virüsün (Parvovirüs B19) replikasyonu ile ilgili olarak aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Mitotik olarak aktif hücrelerde replike olur.",
            "B": "Çoğalmak için eritroid seri öncül hücrelerini tercih eder.",
            "C": "Konak hücre sitoplazmasında replike olur.",
            "D": "Konak hücre DNA polimerazına ihtiyacı vardır.",
            "E": "Konak hücre sitoplazma membranının parçalanması (lizis) ile hücre dışına salınır."
        },
        "answer": "C",
        "explanation": "Parvovirüs B19 tek iplikli (ss) DNA virüsüdür. P antijenini (globosit) reseptör olarak kullanıp eritroid öncüllere girer. Kendi polimerazı olmadığı için S evresindeki bölünen hücrelerin çekirdeğine girer ve replikasyonunu ÇEKİRDEKTE gerçekleştirir (sitoplazmada değil!)."
    },
    72: {
        "subject": "Mikrobiyoloji",
        "topic": "Parazitoloji & Sıtma",
        "question": "Periferik yaymada eritrositlerde Maurer granüllerinin görülmesi, aşağıdaki Plasmodium türlerinden hangisi için spesifiktir?",
        "options": {
            "A": "Plasmodium knowlesi",
            "B": "Plasmodium falciparum",
            "C": "Plasmodium malariae",
            "D": "Plasmodium ovale",
            "E": "Plasmodium vivax"
        },
        "answer": "B",
        "explanation": "Sıtmada periferik yayma eritrosit içi granülleri: Plasmodium falciparum'da Maurer granülleri (ve muz şeklinde gametositler); Plasmodium vivax ve Plasmodium ovale'de Schüffner granülleri; Plasmodium malariae'de ise Ziemann granülleri görülür."
    },
    73: {
        "subject": "Mikrobiyoloji",
        "topic": "İmmünoloji & T Hücre Sitokinleri",
        "question": "Makrofajları aktive ederek intraselüler bakterilerin öldürülmesini sağlayan asıl T lenfosit alt grubu ve salgıladığı sitokin eşleştirmesi aşağıdakilerden hangisidir?",
        "options": {
            "A": "Th1 - IFN-gamma",
            "B": "Th17 - IL-17",
            "C": "Th2 - IL-4",
            "D": "Th2 - IL-13",
            "E": "Treg - TGF-beta"
        },
        "answer": "A",
        "explanation": "Th1 hücreleri başlıca IFN-gamma salgılayarak klasik yoldan makrofaj aktivasyonunu (M1) sağlar. M1 makrofajlar fagozomda reaktif oksijen ve nitrik oksit (NO) üreterek fagositoz yapılmış intraselüler mikroorganizmaları öldürür."
    },
    74: {
        "subject": "Mikrobiyoloji",
        "topic": "Doğal İmmünite & İnflamazom",
        "question": "I. ATP\nII. Ürik asit kristalleri\nIII. Silika parçacıkları\n\nYukarıdakilerden hangileri makrofajlar ve dendritik hücrelerde inflamazom aktivasyonuna neden olan ENDOJEN tehlike sinyallerindendir (DAMP)?",
        "options": {
            "A": "Yalnız I",
            "B": "Yalnız II",
            "C": "I ve II",
            "D": "II ve III",
            "E": "I, II ve III"
        },
        "answer": "C",
        "explanation": "İnflamazom aktivasyonu NLRP3 üzerinden gerçekleşir. Endojen tehlike sinyalleri (DAMP): Hücre dışı ATP, ürik asit kristalleri ve kolesterol kristalleridir. Silika, asbest ve UV radyasyonu ise EKZOJEN tehlike sinyalleridir."
    },
    75: {
        "subject": "Mikrobiyoloji",
        "topic": "İmmünopatoloji & Aşırı Duyarlılık",
        "question": "Yüksek doz penisilin kullanımı sonrasında immün hemolitik anemi tanısı alan bir hastada gelişen ön plandaki aşırı duyarlılık reaksiyonu aşağıdakilerden hangisidir?",
        "options": {
            "A": "Tip 1",
            "B": "Tip 2",
            "C": "Tip 3",
            "D": "Tip 4",
            "E": "Tip 5"
        },
        "answer": "B",
        "explanation": "Penisilin ve kinidin gibi ilaçlar eritrosit zarına bağlanarak hapten gibi davranır; ilaca karşı oluşan IgG ve IgM antikorları komplemanı aktive eder veya fagositoza yol açarak hemoliz yapar. Bu durum Tip 2 (sitotoksik / antikora bağımlı) aşırı duyarlılık reaksiyonudur."
    },
    79: {
        "subject": "Patoloji",
        "topic": "Hücresel Adaptasyon",
        "question": "Aşağıdakilerden hangisi hücresel hipertrofi için örnek oluşturan klinik bir durumdur?",
        "options": {
            "A": "Aort kapak hastalığına bağlı ortaya çıkan kardiyomiyopati",
            "B": "Karaciğer segmentektomi sonrası rezidüel karaciğer dokusunun büyümesi",
            "C": "Uygunsuz östrojen salınımına bağlı ortaya çıkan endometriyal kalınlık artışı",
            "D": "Menopoz döneminde meme asinuslarında görülen değişiklikler",
            "E": "Radius kırığı nedeniyle yapılan alçı sonrası ön kol çizgili kaslarında küçülme"
        },
        "answer": "A",
        "explanation": "Hipertrofi hücre bölünme yeteneği olmayan veya sınırlı olan kalıcı dokularda (çizgili kas ve miyokard) hücre boyutunun ve protein içeriğinin artmasıdır; aort stenozuna bağlı sol ventrikül hipertrofisi tipik örnektir. Karaciğer rejenerasyonu ve endometriyal kalınlaşma ise hiperplazidir."
    },
    81: {
        "subject": "Patoloji",
        "topic": "İnflamasyon & Granülomatöz Reaksiyon",
        "question": "I. Nitrik oksit ve serbest radikaller artar.\nII. TNF (tümör nekroz faktörü) salgılanır.\nIII. Polimorf nüveli lökositler ortama gelir.\n\nTüberküloz enfeksiyonu patogenezinde makrofaj aktivasyonu sonucu gelişen olaylar ile ilgili yukarıdaki ifadelerden hangileri doğrudur?",
        "options": {
            "A": "Yalnız I",
            "B": "Yalnız II",
            "C": "Yalnız III",
            "D": "I ve II",
            "E": "I, II ve III"
        },
        "answer": "D",
        "explanation": "Tüberkülozda IFN-gamma ile aktive olan makrofajlar iNOS sentezleyerek nitrik oksit (NO) ve serbest radikaller üretir, TNF salgılayarak granülom oluşumunu organize eder. Akut nötrofilik infiltrasyon değil, epiteloid histiositler ve Langhans dev hücrelerinden oluşan kronik granülomatöz iltihap gelişir."
    },
    82: {
        "subject": "Patoloji",
        "topic": "Ginekopatoloji & Herediter Kanserler",
        "question": "Anormal uterin kanama sonucunda endometrioid tip endometriyum adenokarsinomu saptanan kadın hastanın soy geçmişinden annesinin genç yaşta metastatik kolon kanseri sonucu öldüğü öğreniliyor. Bu bulgular göz önüne alındığında hastaya aşağıdaki hangi testin yapılması önerilir?",
        "options": {
            "A": "p53 immünohistokimyası",
            "B": "BRAF mutasyonu için genetik analiz",
            "C": "BRCA1 / BRCA2 genlerinin analizi",
            "D": "POLE mutasyonu için sekanslama",
            "E": "Mikrosatelit instabilite (MSI / MMR) araştırılması"
        },
        "answer": "E",
        "explanation": "Genç yaşta kolon kanseri ve endometriyum kanseri birlikteliği Lynch sendromunu (HNPCC) düşündürür. Lynch sendromu DNA mismatch repair (MMR: MLH1, MSH2, MSH6, PMS2) genlerindeki mutasyonlara bağlı mikrosatelit instabilite (MSI-H) ile karakterizedir."
    },
    89: {
        "subject": "Patoloji",
        "topic": "Over & Endometriyum Tümörleri",
        "question": "Altmış yaşındaki kadında endometriyal kalınlık artışı ve sağ overde 8 cm kitle saptanıyor. Biyopsilerde endometriyumda endometrioid karsinom, overde ise erişkin tip granüloza hücreli tümör tespit ediliyor. Aşağıdaki ifadelerden hangisi bu hastada endometriyum ve overdeki tümörlerin ilişkisini en iyi açıklar?",
        "options": {
            "A": "Her iki tümörde mikrosatelit instabilitenin neden olduğu genetik yatkınlık vardır.",
            "B": "Tümör supresör genlerinin mutasyonu sonucu bağımsız 2 ayrı tümör oluşmuştur.",
            "C": "Overde saptanan tümör paraneoplastik sendrom sonucu gelişmiştir.",
            "D": "Endometriyumdaki tümör overdeki tümörden daha önce gelişmiştir.",
            "E": "Overdeki tümörün ürettiği hormon endometriyumda saptanan tümöre neden olmuştur."
        },
        "answer": "E",
        "explanation": "Overin seks kord-stromal tümörlerinden olan Granüloza hücreli tümör yüksek miktarda ÖSTROJEN salgılar. Postmenopozal dönemde devamlı östrojen uyarısı endometriyumda önce hiperplaziye, ardından endometrioid tip endometriyum karsinomuna yol açar."
    },
    94: {
        "subject": "Patoloji",
        "topic": "Hücre Hasarı & Radyasyon Patolojisi",
        "question": "İyonize radyasyonun biyolojik etkileri ile ilgili aşağıdaki ifadelerden hangisi doğrudur?",
        "options": {
            "A": "İyonize radyasyon en belirgin hasarı RNA üzerinde oluşturur.",
            "B": "Hızlı bölünen hücreler hasara daha dayanıklıdır.",
            "C": "Hasar durumunda p53 ekspresyonu azalır.",
            "D": "DNA çift iplik kırıkları sonucu hücre siklus arresti (duraklaması) görülür.",
            "E": "Vasküler hasar ve fibrozis ilk haftalarda ortaya çıkan akut etkilerdendir."
        },
        "answer": "D",
        "explanation": "İyonize radyasyon serbest radikaller ve direkt etkiyle DNA'da çift iplik kırıklarına neden olur. ATM/ATR kinazlar uyarılır, p53 düzeyi artar; p21 aktivasyonu ile hücre G1/S ve G2/M evrelerinde siklus arrestine uğrar."
    },
    95: {
        "subject": "Patoloji",
        "topic": "Tanı Yöntemleri & İmmünohistokimya",
        "question": "Neoplastik bir hücrede diferansiyasyonu belirlemek için hücredeki keratin intermedyer filamanının varlığının gösterilebilmesi amacıyla aşağıdaki yöntemlerden hangisi daha sık kullanılır?",
        "options": {
            "A": "Floresan in situ hibridizasyon (FISH)",
            "B": "Southern blotting",
            "C": "İmmünohistokimya",
            "D": "Yeni nesil dizileme (NGS)",
            "E": "RT-PCR"
        },
        "answer": "C",
        "explanation": "Patoloji rutininde doku kesitlerinde keratin, vimentin, desmin gibi hücre tipi spesifik intermedyer filamanların ve yüzey antijenlerinin saptanmasında antikor temelli İmmünohistokimya (İHK) yöntemi kullanılır."
    },
    96: {
        "subject": "Patoloji",
        "topic": "Karaciğer Patolojisi & Alkol Hasarı",
        "question": "Kronik alkol tüketimi olan bir hastada karaciğerde yağlanma (steatoz) ve hepatosit hasarı patogenezinde aşağıdakilerden hangisinin rolü yoktur?",
        "options": {
            "A": "Trigliserid sentezinin artması",
            "B": "Sitrik asit siklusunu yavaşlatan yüksek NADH/NAD+ oranı",
            "C": "Lipoprotein (VLDL) oluşumu ve salınımının azalması",
            "D": "Dolaşımdaki serbest yağ asitlerinin karaciğere alımının artması",
            "E": "Hepatosit içi glutatyon düzeyinin artması"
        },
        "answer": "E",
        "explanation": "Kronik alkol kullanımı oksidatif strese yol açarak hepatositlerdeki glutatyon depolarını TÜKETİR (glutatyon azalır). Alkol dehidrogenazın NAD+'yi NADH'ye dönüştürmesi yağ asidi oksidasyonunu baskılar ve steatoza neden olur."
    },
    97: {
        "subject": "Patoloji",
        "topic": "Baş-Boyun Patolojisi & HPV",
        "question": "Oral kavite ve orofarinksin HPV ilişkili skuamöz hücreli karsinomlarının klinik özellikleri, HPV ilişkisiz tümörler ile karşılaştırıldığında aşağıdakilerden hangisi HPV ilişkili tümörler için doğrudur?",
        "options": {
            "A": "Oral kavite yerleşimi orofarinkse göre daha sıktır.",
            "B": "Uzak metastaz daha sık görülür.",
            "C": "Kemoterapi ve radyoterapiye yanıtı daha kötüdür.",
            "D": "Daha yaşlı ve sigara içen hastalarda görülür.",
            "E": "Tedavi sonrasında ikinci primer tümör gelişme olasılığı daha düşüktür."
        },
        "answer": "E",
        "explanation": "HPV ilişkili baş-boyun skuamöz karsinomları (özellikle HPV-16); orofarinks ve tonsil kriptlerinde daha sıktır, daha genç yaşta görülür, p16 pozitiftir, kemoradyoterapiye daha duyarlıdır, prognozu belirgin şekilde daha iyidir ve ikinci primer tümör gelişme riski HPV negatiflere göre çok daha düşüktür."
    },
    98: {
        "subject": "Patoloji",
        "topic": "Karaciğer Neoplazileri",
        "question": "Erişkin hasta popülasyonunda non-sirotik karaciğerde en sık görülen malign tümör aşağıdakilerden hangisidir?",
        "options": {
            "A": "Hepatosellüler karsinom, fibrolameller varyant",
            "B": "Metastatik tümör",
            "C": "Kolanjiokarsinom",
            "D": "Hepatosellüler karsinom, şeffaf hücreli varyant",
            "E": "Epitelioid hemanjiyoendotelyoma"
        },
        "answer": "B",
        "explanation": "Karaciğerde hem genel popülasyonda hem de non-sirotik karaciğerde en sık görülen malign tümör METASTATİK tümörlerdir (kolon, akciğer, meme kaynaklı). Karaciğerin en sık görülen primer benign tümörü hemanjiom; primer malign tümörü ise siroz zemininde gelişen HCC'dir."
    },
    100: {
        "subject": "Farmakoloji",
        "topic": "Psikofarmakoloji & İlaç Etkileşimleri",
        "question": "Aşağıdaki ilaçlardan hangisinin lityum renal klirensini ve atılımını artırması en olasıdır?",
        "options": {
            "A": "Hidroklorotiyazid",
            "B": "Asetazolamid",
            "C": "Amilorid",
            "D": "Furosemid",
            "E": "Spironolakton"
        },
        "answer": "B",
        "explanation": "Lityum proksimal tübülden sodyum gibi reabsorbe edilir. Tiazidler ve kıvrım diüretikleri Na kaybı yaparak proksimalden lityum geri emilimini artırır ve lityum toksisitesine yol açar. Proksimal tübülde bikarbonat ve su atılımını artıran Karbonik anhidraz inhibitörleri (Asetazolamid), ozmotik diüretikler (Mannitol) ve teofilin ise lityum atılımını ARTIRIR."
    },
    102: {
        "subject": "Farmakoloji",
        "topic": "Otonom Sinir Sistemi & Antimuskarinikler",
        "question": "Aşağıdaki antimuskarinik ilaçlardan hangisi aşırı aktif mesane, enürezis ve nörojenik mesane durumlarında tercih edilir?",
        "options": {
            "A": "Oksibutinin",
            "B": "Tropikamid",
            "C": "Disiklomin",
            "D": "Homatropin",
            "E": "Hiyosiyamin"
        },
        "answer": "A",
        "explanation": "Oksibutinin, Tolterodin, Darifenasin ve Solifenasin mesane detrusor kasındaki M3 muskarinik reseptörleri bloke ederek mesane spazmlarını azaltır ve aşırı aktif mesane ile enürezis nokturnada kullanılır."
    },
    115: {
        "subject": "Farmakoloji",
        "topic": "Antineoplastik İlaçlar & Hedefe Yönelik Tedavi",
        "question": "Multipl miyelom tedavisinde kullanılan bortezomibin temel etki mekanizması aşağıdakilerden hangisidir?",
        "options": {
            "A": "26S proteazom inhibisyonu",
            "B": "Mitokondriyal Bcl-2 inhibisyonu",
            "C": "PARP enzim inhibisyonu",
            "D": "VEGFR-1 kinaz inhibisyonu",
            "E": "mTOR inhibisyonu"
        },
        "answer": "A",
        "explanation": "Bortezomib; 26S proteazom kompleksini reversibl inhibe eden boronik asit derivesidir. NF-kappaB inhibitörü olan I-kappaB'nin yıkımını önler, NF-kappaB çekirdeğe geçemez ve miyelom hücrelerinde apopitoz tetiklenir."
    },
    116: {
        "subject": "Farmakoloji",
        "topic": "Endokrin Farmakoloji & Danazol",
        "question": "Majör endikasyonu endometriozis olan danazolün farmakolojik özellikleri ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "17-alfa-etiniltestosteron türevidir.",
            "B": "Androjen ve progesteron reseptörlerine bağlanır.",
            "C": "Hemofili ve idiyopatik trombositopenik purpura (İTP) tedavisinde de kullanılır.",
            "D": "Aromataz enzimini indükleyerek meme kanseri hastalarında kullanımı onaylanmıştır.",
            "E": "Kilo alımı, ödem, akne ve seste kalınlaşma başlıca androjenik advers etkilerindendir."
        },
        "answer": "D",
        "explanation": "Danazol zayıf androjenik özellik gösterir ve aromatazı inhibe eder. Androjenik ve teratojenik etkileri nedeniyle meme kanserinde veya gebelerde onaylı DEĞİLDİR; başlıca endometriozis, herediter anjiyoödem ve refrakter İTP tedavisinde kullanılır."
    },
    118: {
        "subject": "Farmakoloji",
        "topic": "Toksikoloji & Şelatörler",
        "question": "I. Arsenik - Dimerkaprol (BAL)\nII. Bakır - Penisilamin\nIII. Kurşun - Dimerkaprol\nIV. Demir - Penisilamin\n\nYukarıdaki ağır metal - antidot/şelatör eşleştirmelerinden hangileri doğrudur?",
        "options": {
            "A": "I ve III",
            "B": "III ve IV",
            "C": "I, II ve III",
            "D": "II ve IV",
            "E": "I, II ve IV"
        },
        "answer": "C",
        "explanation": "Arsenik, cıva ve akut kurşun zehirlenmesinde Dimerkaprol (BAL) kullanılır. Wilson hastalığı ve bakır intoksikasyonunda Penisilamin kullanılır. Demir intoksikasyonunun şelatörü ise Deferoksamin / Deferasiroks'tur (Penisilamin demir için kullanılmaz)."
    },
    125: {
        "subject": "Dahiliye",
        "topic": "Göğüs Hastalıkları & Tromboemboli",
        "question": "Üç hafta önce bacak kırığı nedeniyle alçıya alınan ve istirahat eden 30 yaşındaki erkek hasta, ani başlayan sağ yan ağrısı, nefes darlığı ve taşikardi ile başvuruyor. D-Dimer düzeyi yüksek saptanan bu hastanın kesin tanısı için aşağıdaki tetkiklerden hangisi en uygundur?",
        "options": {
            "A": "Torasik ultrasonografi",
            "B": "Ultrasonografi eşliğinde torasentez ve plevra sıvısının analizi",
            "C": "Toraks yüksek çözünürlüklü bilgisayarlı tomografi (HRCT)",
            "D": "Toraks bilgisayarlı tomografi anjiyografi (BT Pulmoner Anjiyo)",
            "E": "Bronkoskopi"
        },
        "answer": "D",
        "explanation": "İmmobilizasyon sonrası ani göğüs ağrısı, nefes darlığı, taşikardi ve D-dimer yüksekliği pulmoner tromboemboliyi (PTE) düşündürür. PTE şüphesinde güncel kılavuzlarda ilk tercih edilen ve altın standart kabul edilen tanı yöntemi Kontrastlı BT Pulmoner Anjiyografidir."
    },
    151: {
        "subject": "Pediatri",
        "topic": "Dermatoloji & Deri Lezyonları",
        "question": "Aşağıdakilerden hangisi benign bir deri tümörüdür?",
        "options": {
            "A": "Dermatofibrom",
            "B": "Bazal hücreli karsinom",
            "C": "Meme başının Paget hastalığı",
            "D": "Skuamöz hücreli karsinom",
            "E": "Malign melanom"
        },
        "answer": "A",
        "explanation": "Dermatofibrom (benign fibröz histiyositom); deride en sık görülen selim mezenkimal lezyonlardandır, tipik olarak lezyon sıkıştırıldığında çökme (dimple sign / gamze belirtisi) gösterir. Diğer seçenekler malign deri tümörleridir."
    },
    161: {
        "subject": "Pediatri",
        "topic": "Nükleer Tıp & Radyofarmasötikler",
        "question": "Aşağıdaki radyoizotoplardan hangisi hem beta partikülü emisyonu hem de gama emisyonu yapma özelliklerinin olması nedeniyle tedavide kullanımının yanı sıra görüntüleme amacıyla da kullanılır?",
        "options": {
            "A": "32P (32-Fosfor)",
            "B": "131I (131-İyot)",
            "C": "89Sr (89-Stronsiyum)",
            "D": "90Y (90-Yitriyum)",
            "E": "186Re (186-Renyum)"
        },
        "answer": "B",
        "explanation": "131-İyot (I-131); yaydığı beta parçacıklarıyla tiroid dokusunda ablatif tedavi (radyoaktif iyot tedavisi) sağlarken, eş zamanlı yaydığı gama fotonları sayesinde gama kameralarda tüm vücut sintigrafik görüntülemesine olanak tanıyan ideal bir teranostik ajandır."
    },
    169: {
        "subject": "Pediatri",
        "topic": "Neonatoloji & İntrauterin Gelişme",
        "question": "Simetrik intrauterin büyüme kısıtlılığı (IUGR) olan bebekler ile ilgili aşağıdaki ifadelerden hangisi doğrudur?",
        "options": {
            "A": "Fetal malnütrisyon belirgindir.",
            "B": "Baş çevresi vücuda göre korunmuştur.",
            "C": "Etiyolojide plasental yetmezlik ön plandadır.",
            "D": "İntrauterin büyüme kısıtlılığı olan olguların çoğunluğunu oluşturur.",
            "E": "İlk trimesterdeki konjenital enfeksiyonlar fetal nedenler arasındadır."
        },
        "answer": "E",
        "explanation": "Simetrik IUGR (Tip 1): Gebeliğin erken evrelerinde (ilk 16 hafta) hücre hiperplazisinin etkilendiği durumlarda (kromozomal anomaliler ve TORCH konjenital enfeksiyonları) gelişir. Hem baş çevresi hem kilo orantılı küçüktür (baş çevresi korunmaz). Geç dönem plasental yetmezlik ise baş çevresinin korunduğu Asimetrik IUGR yapar."
    },
    179: {
        "subject": "Pediatri",
        "topic": "Pediatrik Hematoloji & Kemik İliği Yetmezliği",
        "question": "Diamond-Blackfan anemisi ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Eritrositler makrositiktir.",
            "B": "HbF düzeyi artmıştır.",
            "C": "Eritrosit adenozin deaminaz (ADA) düzeyi artmıştır.",
            "D": "Klinik bulgular genellikle ilk dekattan (10 yaşından) sonra başlar.",
            "E": "Retikülosit oranı belirgin olarak azalmıştır."
        },
        "answer": "D",
        "explanation": "Diamond-Blackfan anemisi (konjenital saf eritroid aplazisi); ribozomopati (RPS19 mutasyonu) sonucu gelişir. Olguların %90'ı hayatın İLK YAŞINDA (genellikle 2-6. aylarda) derin anemi ile tanı alır; ilk dekattan sonra başlamaz. Makrositer anemi, retikülositopeni ve yüksek eritrosit ADA aktivitesi tipiktir."
    },
    183: {
        "subject": "Genel Cerrahi",
        "topic": "Akut Batın & Pankreas",
        "question": "Özellikle sırta yayılan şiddetli karın ağrısı ile gelen ve 3 gün önce bisikletten düşme öyküsü olan 12 yaşındaki erkek hastada en olası tanı aşağıdakilerden hangisidir?",
        "options": {
            "A": "Kolelitiyazis",
            "B": "Akut kolesistit",
            "C": "Akut pankreatit",
            "D": "Akut kolanjit",
            "E": "Akut apandisit"
        },
        "answer": "C",
        "explanation": "Çocukluk çağında künt batın travması (özellikle bisiklet gidonu travması), pankreasın omurga üzerinde sıkışması sonucu travmatik AKUT PANKREATİTE yol açar. Epigastrik kuşak tarzı ve sırta vuran ağrı ile serum amilaz/lipaz yüksekliği tipiktir."
    },
    194: {
        "subject": "Genel Cerrahi",
        "topic": "Postoperatif Komplikasyonlar",
        "question": "Seksen yaşındaki diyabetik erkek hastada sabah erken saatlerde laparoskopik kolesistektomi yapılıyor. Postoperatif dönemde idrar yapamama, suprapubik ağrı ve palpasyonda glob vezikale saptanan hastada en olası tanı aşağıdakilerden hangisidir?",
        "options": {
            "A": "Üriner retansiyon",
            "B": "İntraabdominal apse",
            "C": "Brid ileus",
            "D": "Safra kaçağı",
            "E": "Elektrolit bozukluğu"
        },
        "answer": "A",
        "explanation": "Genel anestezi sonrası erken dönemde idrar çıkaramama, suprapubik dolgunluk ve ağrı ÜRİNER RETANSİYONDUR. Yaşlı erkek hastalarda (özellikle BPH zemininde) ve opioid kullanımı sonrasında sık gelişir; mesane kateterizasyonu ile tedavi edilir."
    },
    197: {
        "subject": "Genel Cerrahi",
        "topic": "Perioperatif Yönetim & Antikoagülanlar",
        "question": "Antikoagülanlar ve acil durumlarda antikoagülan etkinin geri dönüşümü için kullanılabilecek antidotlarla ilgili aşağıdaki eşleştirmelerden hangisi yanlıştır?",
        "options": {
            "A": "Varfarin - Taze donmuş plazma",
            "B": "Klopidogrel - Trombosit süspansiyonu",
            "C": "Heparin - Protamin sülfat",
            "D": "Varfarin - K vitamini",
            "E": "Dabigatran - Desmopresin"
        },
        "answer": "E",
        "explanation": "Direkt trombin inhibitörü olan Dabigatranın spesifik monoklonal antidotu İDARUSİZUMAB'dır (Praxbind). Desmopresin von Willebrand hastalığı ve üremik kanamalarda kullanılır, dabigatranı geri çevirmez."
    },
    200: {
        "subject": "Genel Cerrahi",
        "topic": "Biliyer Sistem Cerrahisi",
        "question": "Primer sklerozan kolanjit (PSK) tanı ve tedavisi ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?",
        "options": {
            "A": "Yorgunluk, kaşıntı ve sarılık hastaların başvuru nedenlerindendir.",
            "B": "İnflamatuvar bağırsak hastalığı olanlarda karaciğer enzim bozukluğunda PSK düşünülmelidir.",
            "C": "ERCP'de tespih tanesi görünümü tanı koydurucudur.",
            "D": "Ülseratif kolitli olgularda kolektomi yapılması PSK'nin ilerlemesini durdurur.",
            "E": "Karaciğer transplantasyonu yapılan hastalarda PSK rekürrens gösterebilir."
        },
        "answer": "D",
        "explanation": "PSK olgularının %70-80'inde Ülseratif Kolit eşlik eder; ancak PSK bağımsız seyreder. Kolektomi yapılması karaciğerdeki PSK hastalığının progresyonunu DURDURMAZ."
    },
    205: {
        "subject": "Genel Cerrahi",
        "topic": "Endokrin Cerrahi & Tiroidektomi",
        "question": "Total tiroidektomi cerrahisi sonrası en sık görülen komplikasyon aşağıdakilerden hangisidir?",
        "options": {
            "A": "Kalıcı rekürren laringeal sinir hasarı",
            "B": "Superior laringeal sinir hasarı",
            "C": "Pnömotoraks",
            "D": "Geçici hipoparatiroidizm (hipokalsemi)",
            "E": "Duktus torasikus yaralanması"
        },
        "answer": "D",
        "explanation": "Total tiroidektomi sonrasında en sık rastlanan komplikasyon (%10-25 sıklıkla) paratiroid bezlerinin geçici iskemisine veya cerrahi travmasına bağlı GEÇİCİ HİPOPARATİROİDİZM ve hipokalsemidir. Çoğu hasta haftalar-aylar içinde düzelir."
    },
    208: {
        "subject": "Genel Cerrahi",
        "topic": "İnce Bağırsak Cerrahisi",
        "question": "Elli iki yaşındaki erkek hastada, travma nedeniyle Treitz ligamanının 30 cm altından 1 metre uzunluğunda jejunum segmenti eksize ediliyor. Aşağıdakilerden hangisinin bu hastada ileride kısa bağırsak sendromu gelişme riskini artırması en az olasıdır?",
        "options": {
            "A": "Terminal ileumu içeren segmental rezeksiyon yapılması",
            "B": "İkinci kez ince bağırsak rezeksiyonu sonucu toplamda 225 cm ince bağırsak kalması",
            "C": "Total kolektomi yapılması",
            "D": "Hastanın Crohn hastalığı tanısı alması",
            "E": "İleoçekal valvin rezeke edilmesi"
        },
        "answer": "B",
        "explanation": "Kısa bağırsak sendromu genellikle kalan fonksiyonel ince bağırsak uzunluğunun 150-200 cm'nin altına inmesi durumunda ortaya çıkar. Kalan ince bağırsak uzunluğunun 225 cm olması kısa bağırsak sendromu riskini artırmaz."
    },
    212: {
        "subject": "Genel Cerrahi",
        "topic": "Fıtık Cerrahisi & İnguinal Anatomi",
        "question": "Direkt ve indirekt inguinal hernilerin cerrahi ayrımında kullanılan referans anatomik yapı aşağıdakilerden hangisidir?",
        "options": {
            "A": "Musculus rectus abdominis lateral kenarı",
            "B": "İnferior epigastrik arter ve ven",
            "C": "İnguinal ligaman",
            "D": "Median umbilikal ligaman",
            "E": "Pektineal (Cooper) ligaman"
        },
        "answer": "B",
        "explanation": "İnferior epigastrik damarlar referanstır: Fıtık kesesi inferior epigastrik damarların LATERALİNDE ise İndirekt fıtık (derin inguinal halkadan çıkar); MEDİALİNDE ise Direkt fıtık (Hesselbach üçgeninden çıkar)."
    },
    216: {
        "subject": "Genel Cerrahi",
        "topic": "Dalak Cerrahisi",
        "question": "Aksesuar dalağın en sık bulunduğu lokalizasyon aşağıdakilerden hangisidir?",
        "options": {
            "A": "Pankreas kuyruğu arkası",
            "B": "Mezenter",
            "C": "Splenik hilus",
            "D": "Büyük omentum",
            "E": "Splenokolik ligaman"
        },
        "answer": "C",
        "explanation": "Aksesuar dalak (splenunculus) en sık (%75-80 oranında) DALAK HİLUSUNDA ve gastrosplenik ligaman çevresinde yerleşir. İTP nedeniyle yapılan splenektomilerde relapsı önlemek için hilustaki aksesuar dalaklar aranmalıdır."
    },
    219: {
        "subject": "Kadın Hastalıkları ve Doğum",
        "topic": "Anestezi & Obstetrik Analjezi",
        "question": "Nöroaksiyel blok (spinal / epidural anestezi) yapılırken orta hatta iğne ile ilk geçilen ligaman aşağıdakilerden hangisidir?",
        "options": {
            "A": "Supraspinöz ligaman",
            "B": "İnterspinöz ligaman",
            "C": "Ligamentum flavum",
            "D": "Anterior longitudinal ligaman",
            "E": "Posterior longitudinal ligaman"
        },
        "answer": "A",
        "explanation": "Orta hat lomber ponksiyonda iğnenin sırasıyla geçtiği tabakalar: 1. Cilt, 2. Cilt altı yağ dokusu, 3. Supraspinöz ligaman (ilk geçilen ligaman), 4. İnterspinöz ligaman, 5. Ligamentum flavum, 6. Epidural aralık, 7. Dura mater ve araknoid mater."
    },
    220: {
        "subject": "Kadın Hastalıkları ve Doğum",
        "topic": "Toksikoloji & Kolinerjik Toksidrom",
        "question": "Aşağıdaki ajanlara bağlı zehirlenmelerin hangisinde bradikardi, bronkore ve bronkospazm görülmesi en olasıdır?",
        "options": {
            "A": "Opioidler",
            "B": "Beta blokörler",
            "C": "Digoksin",
            "D": "Trisiklik antidepresanlar",
            "E": "Organofosfatlar"
        },
        "answer": "E",
        "explanation": "Organofosfatlar asetilkolinesteraz enzimini geri dönüşümsüz inhibe ederek kolinerjik krize yol açar. Muskarinik aşırı uyarı: 'Killer B'ler (Bradikardi, Bronkospazm, Bronkore) ile aşırı tükürük, lakrimasyon, miyozis ve diyaredir."
    },
    222: {
        "subject": "Pediatri",
        "topic": "Pediatrik Cerrahi & GİS Anomalileri",
        "question": "Hipertrofik pilor stenozu olan bir süt çocuğunda aşağıdakilerden hangisinin görülmesi diğerlerinden daha az olasıdır?",
        "options": {
            "A": "Safralı kusma",
            "B": "Fışkırır tarzda kusma",
            "C": "Hipokloremik hipokalemik metabolik alkaloz",
            "D": "Epigastrik 'zeytin' kitle palpasyonu (olive sign)",
            "E": "Dehidratasyon ve kilo kaybı"
        },
        "answer": "A",
        "explanation": "Hipertrofik pilor stenozunda darlık ampulla vateri'nin proksimalindedir. Bu nedenle kusma KESİNLİKLE SAFRASIZDIR. Safralı kusma olması duodenal atrezi gibi pilor distali obstrüksiyonları düşündürür."
    },
    227: {
        "subject": "Küçük Stajlar",
        "topic": "KBB & Nöroşirürji (Sinüzit Komplikasyonları)",
        "question": "Üç gündür akut sinüzit semptomları olan 10 yaşındaki erkek hastada bilateral orbital ağrı, kemozis ve proptozis ile 3, 4, 5 (V1-V2) ve 6. kraniyal sinir paralizisi gelişiyor. Bu hasta için en olası tanı aşağıdakilerden hangisidir?",
        "options": {
            "A": "Preseptal selülit",
            "B": "Orbital selülit",
            "C": "Orbital apse",
            "D": "Kavernöz sinüs tromboflebiti",
            "E": "Subperiosteal apse"
        },
        "answer": "D",
        "explanation": "Akut sinüzit zemininde gelişen kemozis, proptozis, oftalmopleji ve bilateral kraniyal sinir (III, IV, V1, V2, VI) tutulumu Kavernöz Sinüs Trombozu / Tromboflebitinin klasik bulgusudur."
    },
    230: {
        "subject": "Kadın Hastalıkları ve Doğum",
        "topic": "Perinatoloji & Rh Uyuşmazlığı",
        "question": "Yirmi beş yaşındaki gebe hastanın kan grubunun A Rh (-), eşinin kan grubunun ise A Rh (+) olduğu ve maternal Anti-D IgG titresinin 1/4 olduğu öğreniliyor. Bu gebe için bir sonraki aşamada yapılması önerilen en uygun yaklaşım aşağıdakilerden hangisidir?",
        "options": {
            "A": "Paternal zigosite (babanın Rh genotipi) tayini",
            "B": "Hemen profilaktik Anti-D immünoglobulin verilmesi",
            "C": "Maternal zigosite tayini",
            "D": "Amniyotik sıvıda bilirubin ölçümü (delta OD450)",
            "E": "Koryon villus örneklemesi ile fetal genotip tayini"
        },
        "answer": "A",
        "explanation": "İndirekt Coombs pozitif ve antikor titresi kritik düzeyin altındaysa ilk adım babanın zigosite durumunun belirlenmesidir. Baba homozigot DD ise fetüs kesinlikle Rh(+) olacaktır ve takip gerekir; baba heterozigot Dd ise fetüsün %50 ihtimalle Rh(-) olma şansı vardır."
    },
    231: {
        "subject": "Kadın Hastalıkları ve Doğum",
        "topic": "Gebelikte Kalp Hastalıkları",
        "question": "I. Dinlenme halinde semptom yoktur.\nII. Evin içinde bir odadan diğer odaya yürürken çabuk yorulma, çarpıntı, dispne gibi şikayetler olur.\nIII. Merdiven inerken semptom yoktur.\n\nYukarıdakilerden hangileri, 'Gebelikte Kalp Hastalıkları NYHA (New York Heart Association) Fonksiyonel Sınıflaması'na göre Sınıf III semptomlar ile uyumludur?",
        "options": {
            "A": "Yalnız II",
            "B": "I ve II",
            "C": "I ve III",
            "D": "II ve III",
            "E": "I, II ve III"
        },
        "answer": "B",
        "explanation": "NYHA Sınıf III: İstirahatte semptom yoktur (I doğru). Ancak olağan dışı hafif fiziksel aktivitelerde (evin içinde odadan odaya yürümek gibi normalden daha az aktiviteyle) belirgin yorgunluk, çarpıntı ve dispne ortaya çıkar (II doğru). Merdiven inmek gibi eforlarda semptom olmaması Sınıf III ile uyumlu değildir."
    }
}

def main():
    with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} questions.")
    cleaned_list = []

    for idx, q in enumerate(data):
        qnum = q.get('original_num')
        qid = q.get('id', f"mart2023_q{qnum}")

        # Check if we have curated data for this question
        if qnum in CURATED_DATA:
            cur = CURATED_DATA[qnum]
            new_q = {
                "id": qid,
                "original_num": qnum,
                "exam": "Mart 2023 TUS",
                "period": "Mart 2023",
                "subject": cur["subject"],
                "topic": cur["topic"],
                "question": purify_text(cur["question"]),
                "options": {k: purify_text(v) for k, v in cur["options"].items()},
                "answer": cur["answer"],
                "explanation": purify_text(cur["explanation"])
            }
        else:
            # Algorithmic purification
            raw_q = q.get("question", "")
            raw_expl = q.get("explanation", "")
            
            # Clean stem from prepended diagrams or copyright
            clean_q = purify_text(raw_q)
            # Remove any prepended "Doğru cevap: X"
            clean_q = re.sub(r'^.*Doğru\s*cevap\s*:\s*[A-E]\s*', '', clean_q, flags=re.IGNORECASE)
            
            clean_expl = purify_text(raw_expl)
            clean_opts = {k: purify_text(v) for k, v in q.get("options", {}).items()}
            
            sub = q.get("subject", "Genel TUS")
            top = q.get("topic", sub)
            if top == sub:
                top = f"{sub} Genel"
                
            new_q = {
                "id": qid,
                "original_num": qnum,
                "exam": "Mart 2023 TUS",
                "period": "Mart 2023",
                "subject": sub,
                "topic": top,
                "question": clean_q,
                "options": clean_opts,
                "answer": q.get("answer", "A"),
                "explanation": clean_expl
            }

        cleaned_list.append(new_q)

    # Save to questions_mart2023.json
    out_path = 'cikmis_sorular/virtual_db/questions_mart2023.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_list, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully wrote {len(cleaned_list)} clean questions to {out_path}")

if __name__ == '__main__':
    main()
