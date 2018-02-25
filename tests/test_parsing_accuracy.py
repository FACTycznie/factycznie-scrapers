import unittest
import re

import scrapy
from datetime import date

from factscraper import analyze_url, downloader, InvalidArticleError

class _TestArticle:
    def __init__(self, initial_url, clean_url, domain, title, text, 
                 publish_date, sources, authors):
        self.initial_url = initial_url
        self.clean_url = clean_url
        self.domain = domain
        self.title = title
        self.text = text
        self.publish_date = publish_date
        self.sources = sources
        self.authors = authors

test_articles = [
    _TestArticle(
        "http://fakty.interia.pl/swiat/news-wenezuela-powstal-czarny-rynek-krwi,nId,2549737",
        "http://fakty.interia.pl/swiat/news-wenezuela-powstal-czarny-rynek-krwi,nId,2549737",
        "fakty.interia.pl",
        "Wenezuela: Powstał czarny rynek krwi",
        """Ochrona zdrowia, której dostępność dla najuboższych była jednym z
        głównych haseł "rewolucji boliwariańskiej" zainicjowanej 20 lat temu
        przez prezydenta Hugo Chaveza, stała się kolejną ofiarą kryzysu
        gospodarczego w Wenezueli: powstał tam czarny rynek krwi. Wskutek
        załamania się wenezuelskiej waluty - boliwara, które wyraża się w
        czterocyfrowej inflacji, przestało w kraju działać 70 proc. publicznych
        banków krwi - ogłosiła w tym tygodniu organizacja pod nazwą Koalicja w
        Obronie Prawa do Zdrowia i Życia (Codevida). Sekretarz generalna
        Wenezuelskiego Towarzystwa Hematologicznego dr Maribel Melendez
        oświadczyła, że "w instytucjach publicznej służby zdrowia wykryto
        osoby, które starają się ciągnąć zyski z braków w bankach krwi". Dr
        Melendez podkreśla, że to państwo wenezuelskie jest odpowiedzialne za
        powstałą sytuację, ponieważ z braku środków od września zaprzestało
        asygnowania odpowiednich środków na cele związane z pozyskiwaniem krwi
        od krwiodawców. Wskutek tego niektóre spośród 23 stanów Wenezueli
        pozostały bez zapasów krwi. Odczynniki chemiczne służące do analizy
        krwi nie są produkowane w kraju i muszą być importowane, a państwo,
        które ma monopol na pozyskiwanie dewiz, drastycznie zredukowało ich
        import i przydziały dla publicznych i prywatnych placówek ochrony
        zdrowia. Według informacji Melendez, w szpitalach coraz częściej
        powtarza się sytuacja, gdy przy łóżku pacjenta przygotowywanego do
        operacji pojawia się osoba handlująca krwią i proponuje choremu jej
        dostarczenie za określoną kwotę. Według hiszpańskiej agencji EFE,
        wolnorynkowa cena pojemnika z krwią do przeszczepu dla jednego
        pacjenta, którą szpital powinien mu teoretycznie zapewnić bez opłaty,
        wynosi obecnie 4 333 000 boliwarów, tj. ok 140 dolarów. Prezes
        Wenezuelskiej Federacji Medycznej Douglas Leon Natera oświadczył, że
        banki krwi "zbankrutowały", a setki tysięcy pacjentów "znalazły się w
        niepewnej sytuacji".
        """,
        date(year=2018, month=2, day=24),
        ['PAP'],
        []),
    _TestArticle(
        "http://fakty.interia.pl/swiat/news-izraelskie-media-polski-rzad-zamraza-ustawe-o-ipn,nId,2549714",
        "http://fakty.interia.pl/swiat/news-izraelskie-media-polski-rzad-zamraza-ustawe-o-ipn,nId,2549714",
        "fakty.interia.pl",
        "Izraelskie media: Polski rząd zamraża ustawę o IPN",
        """Po naciskach Izraela Polska ugięła się i zamraża ustawę o IPN -
        piszą w sobotę izraelskie media. Według nich, oczekuje się, że polska
        delegacja przyjedzie do Izraela w najbliższych dniach, by wypracować
        porozumienie w tej sprawie. Przedstawiciele izraelskiego rządu
        powiedzieli Polskiemu Radiu, że w ostatnich dniach doszło do spotkania
        izraelskiej ambasador w Polsce Anny Azari z polskim ministrem
        sprawiedliwości Zbigniewem Ziobrą. Według relacji strony izraelskiej,
        minister sprawiedliwości i prokurator generalny miał poinformować, że
        nowelizacja ustawy będzie dotyczyła nie tylko artystów i naukowców, ale
        również ocalałych z Holocaustu i dziennikarzy. Strona izraelska
        poinformowała, że uznaje słowa ministra Zbigniewa Ziobry za wiążące.
        Dyrektor generalny izraelskiego resortu spraw zagranicznych Juwal Rotem
        - cytowany przez "Times of Israel" - powiedział, że decyzja polskich
        władz w sprawie ustawy o IPN to "sukces izraelskiej dyplomacji", który
        jest wynikiem intensywnej debaty między Jerozolimą a Warszawą, jaka
        toczyła się w ostatnich tygodniach. "Jerusalem Post" pisze, że
        "zamrożenie ustawy" jest wynikiem "presji Izraela". Podaje, że polski
        minister sprawiedliwości Zbigniew Ziobro "zapowiedział, że ustawa nie
        wejdzie w życie, zanim kwestii tej nie rozpatrzy polski Trybunał
        Konstytucyjny". Według "Jerusalem Post" Ziobro poinformował o tym w
        wywiadzie dla polskich mediów i dodał, że opinia Trybunału
        Konstytucyjnego w tej sprawie jest nieodzowna, aby prokuratorzy
        wiedzieli, w jaki sposób stosować przepisy. Dziennik "Haaretz" pisze z
        kolei, że do Izraela ma wkrótce przybyć polska delegacja, aby
        wypracować kompromis w sprawie ustawy o IPN. Informację potwierdził
        również reporter TVN24 Jacek Tacik. Wczoraj minister sprawiedliwości
        Zbigniew Ziobro powiedział PAP, że znowelizowana ustawa o IPN ma
        chronić państwo polskie i naród jako całość przed kłamliwymi
        oskarżeniami o udział w niemieckich zbrodniach, a nie służyć zacieraniu
        odpowiedzialności pojedynczych osób lub grup. "Nie będzie kar dla
        świadków historii, naukowców czy dziennikarzy za przywoływanie
        bolesnych faktów z naszej historii" - mówił Zbigniew Ziobro. Również
        minister spraw zagranicznych Jacek Czaputowicz mówił w TVP Info, że
        pomiędzy wejściem w życie nowelizacji a orzeczeniem Trybunału
        Konstytucyjnego nie dojdzie do tego, że strona Polska będzie ścigać
        świadków Holokaustu czy autorów publikacji naukowych na ten temat.
        Nowelizacja ustawy o IPN zakłada miedzy innymi karę do trzech lat
        więzienia za "publicznie i wbrew faktom" przypisywanie polskiemu
        narodowi lub państwu polskiemu odpowiedzialności lub
        współodpowiedzialności za zbrodnie popełnione przez III Rzeszę
        Niemiecką lub inne zbrodnie przeciwko ludzkości, pokojowi i zbrodnie
        wojenne. Ustawę będzie badał też Trybunał Konstytucyjny po wniosku
        prezydenta Andrzeja Dudy.""",
        date(year=2018, month=2, day=24),
        ['IAR', 'PAP', 'INTERIA.PL'],
        []),
    _TestArticle(
        "http://nt.interia.pl/raporty/raport-zagadki-przyrody/strona-glowna/news-juz-wiadomo-dlaczego-nietoperze-sa-odporne-na-niebezpieczne-,nId,2549307",
        "http://nt.interia.pl/raporty/raport-zagadki-przyrody/strona-glowna/news-juz-wiadomo-dlaczego-nietoperze-sa-odporne-na-niebezpieczne-,nId,2549307",
        "nt.interia.pl",
        "Już wiadomo, dlaczego nietoperze są odporne na niebezpieczne wirusy",
        """Pojedyncza mutacja w genie o nazwie Sting może być jednym z powodów,
        dla których nietoperze są odporne na skutki działania potencjalnie
        śmiercionośnych wirusów, takich jak Ebola. Chińscy naukowcy wykazali,
        że gen Sting u nietoperzy indukuje produkcję niższych poziomów
        interferonu, który sygnalizuje, że organizm jest atakowany przez
        wirusa. Za duże stężenie interferonu wiąże się z wystąpieniem poważnych
        objawów obserwowanych w wielu zakażeniach wirusowych. Ale dzięki
        specjalnej mutacji, nietoperze mogą z tym walczyć. Powszechnie wiadomo
        bowiem, że nietoperze mogą być nosicielami wielu niebezpiecznych
        wirusów (Marburg, Ebola, Nipah) i jednocześnie nie cierpieć z tego
        powodu. - Interesowało nas, dlaczego układ odpornościowy nietoperzy
        może radzić sobie z tak wieloma śmiercionośnymi wirusami - powiedział
        prof. Peng Zhou z Instytutu Wirusologii w Wuhan. Zazwyczaj w
        mechanizmach odpornościowych na infekcje wirusowe biorą udział
        przeciwciała i limfocyty T. Rozpoznają one wirusy, które poznały w
        wyniku szczepień ochronnych lub wcześniej przebytych infekcji. Ale
        wirusowych najeźdców można także zwalczać dzięki odporności wrodzonej.
        Kiedy wirus infekuje komórkę, pozostawia wiele znaków
        charakterystycznych, a te są wykrywane przez białka, które włączają
        produkcję interferonu. Wczesne objawy, które wiążemy z infekcją
        wirusową - gorączka, bóle mięśniowe i zmęczenie - są spowodowane
        działaniem interferonu. Interferon uruchamia powstawanie innych
        cząsteczek, które wykazują bezpośredni efekt antywirusowy. Okazuje się
        jednak, że za duże ilości interferonu także szkodzą. To właśnie przez
        ten szczegół niektóre wirusy, takie jak Ebola czy SARS są
        niebezpieczne. - Początkowo myśleliśmy, że nietoperze mają bardzo silny
        układ odpornościowy, ale po dokładniejszym badaniu genomu nietoperzy
        stwierdziliśmy, że wykorzystywany przez nie mechanizm jest wyjątkowy -
        powiedział prof. Zhou. Szczególnie ważną rolę w walce z wirusami
        odgrywa gen Sting. Dzięki niemu możliwe jest wykrywanie obcego DNA w
        miejscu, w którym normalnie nie powinno go być, czyli w cytoplazmie
        komórki. Niektóre badania sugerują także, że dzięki Sting nietoperze
        mogą wykrywać RNA - alternatywny materiał genetyczny często
        wykorzystywany przez wirusy. - Odkryliśmy, że gen Sting wpływa na
        wytwarzanie interferonu przez nietoperze, co utrudnia
        rozprzestrzenianie się wirusów - dodał prof. Zhou. Naukowcy nie są
        jednak pewni, czy stłumienie wytwarzania interferonu przez zmieniony
        gen Sting, zapewnia bezpośrednią ochronę przed niebezpiecznymi
        wirusami. Konieczne są dalsze badania do potwierdzenia tych
        rewelacji.""",
        date(year=2018, month=2, day=24),
        ['INTERIA.PL'],
        []),
    _TestArticle(
        "https://wiadomosci.onet.pl/swiat/francja-od-stycznia-udaremniono-dwa-ataki-terrorystyczne/gd12e97",
        "https://wiadomosci.onet.pl/swiat/francja-od-stycznia-udaremniono-dwa-ataki-terrorystyczne/gd12e97",
        "wiadomosci.onet.pl",
        "Francja: od stycznia udaremniono dwa ataki terrorystyczne",
        """Od stycznia we Francji udaremniono dwa planowane ataki
        terrorystyczne, w tym jeden na obiekt sportowy, a drugi na siły
        wojskowe - poinformował w niedzielę francuski minister spraw
        wewnętrznych Gerard Collomb. W wywiadzie dla radia Europe 1, telewizji
        C-News i dziennika ekonomicznego "Les Echos" minister powiedział
        ogólnie, że zamachy te udaremniono "na południu" i "na zachodzie"
        Francji. - Celem była młodzież - dodał, odnosząc się do planu ataku na
        - jak to ujął - "duży obiekt sportowy". W wywiadzie dla radia Europe 1,
        telewizji C-News i dziennika ekonomicznego "Les Echos" minister
        powiedział ogólnie, że zamachy te udaremniono "na południu" i "na
        zachodzie" Francji. - Celem była młodzież - dodał, odnosząc się do
        planu ataku na - jak to ujął - "duży obiekt sportowy". Szef
        francuskiego MSW powiadomił, że podejrzane osoby zostały zatrzymane i
        przebywają w areszcie. - W ten sposób udało nam się udaremnić te plany
        - dodał Collomb, ale nie ujawnił więcej szczegółów na temat
        aresztowania, ani celów ataków. Wskazał jedynie, że chodzi o osoby
        widniejące już w tzw. kartotece osób zradykalizowanych (FSPRT), która
        we Francji prowadzona jest od 2015 roku i ma zasadnicze znaczenie dla
        walki z terroryzmem. Figurują w niej osoby, które stosują przemoc bądź
        mogą się do niej uciekać. Są tam dane osobowe, adres, opis sytuacji
        prawnej, ewentualna opinia psychiatryczna, informacje o kontaktach z
        innymi radykałami. Minister Collomb poinformował również, że w
        niedzielę we Francji zostały zamknięte trzy meczety - dwa na
        południowym wschodzie kraju i jeden w regionie paryskim - "ponieważ
        głoszono w nich pochwałę terroryzmu". Według oficjalnych danych we
        Francji w 2017 roku udaremniono dwadzieścia ataków terrorystycznych.""",
        date(year=2018, month=2, day=25),
        [], # Actually this should be ["Gerard Collomb"] or ["Europe 1",
        # "C-News", "Les Echos"] or even ["Francuskie MSW"] but it's
        # too difficult to retrieve for now
        [])

    ]

class TestDownload(unittest.TestCase):
    """This test case checks if `factscraper.downloader` works."""
    def setUp(self):
        self.test_url = "https://wroclaw.onet.pl/tragiczny-wypadek-we-wroclawiu-nie-zyje-mezczyzna/v3kvx88"

    def test_download(self):
        download_result = downloader.download(self.test_url)
        self.assertIsInstance(
            download_result,
            scrapy.http.HtmlResponse)
        self.assertIn(bytes("article", 'utf-8'), download_result.body)

class TestArticleDetection(unittest.TestCase):
    """This test case checks how accurately we can detect if a webpage
    contains an article.
    """
    def setUp(self):
        self.correct_urls = [
            "https://wroclaw.onet.pl/tragiczny-wypadek-we-wroclawiu-nie-zyje-mezczyzna/v3kvx88",
            "https://wiadomosci.onet.pl/swiat/francja-od-stycznia-udaremniono-dwa-ataki-terrorystyczne/gd12e97a",
            "http://www.se.pl/wiadomosci/polityka/zabiora-kosmonaucie-gwiazdy-miroslaw-hermaszewski-nie-bedzie-juz-generalem_1041634.html",
            "http://wiadomosci.gazeta.pl/wiadomosci/7,114883,23069152,lodzcy-straznicy-zabrali-kobiete-do-izby-wytrzezwien-nie-byla.html#Z_Czolka3Img"]
        self.invalid_urls = [
            "http://wiadomosci.gazeta.pl/wiadomosci/0,156046.html#TRNavSST",
            "http://weekend.gazeta.pl/weekend/0,0.html",
            "http://fakty.interia.pl/opinie",
            "http://firma.interia.pl/regulamin",
            "http://fakty.interia.pl/inne-serwisy",
            "https://wp.pl/",
            "http://kultura.gazeta.pl/kultura/56,114526,22658501,najlepsze-koncerty-wystawy-i-wydarzenia-z-calej-polski-tym.html",
        ]

    def test_correct_urls(self):
        # This only tests whether or not 
        for url in self.correct_urls:
            try:
                analyze_url(url)
            except InvalidArticleError:
                self.fail("analyze_url raised InvalidArticleError on an "
                          "actual article.")

    def test_invalid_urls(self):
        # This only tests whether or not 
        for url in self.invalid_urls:
            self.assertRaises(InvalidArticleError, analyze_url, url)


# Download them now so we don't have to redownload them for each test
_downloaded_articles = []
for test_article in test_articles:
    try:
        _downloaded_articles.append(analyze_url(test_article.initial_url))
    except InvalidArticleError:
        pass

class TestGeneralAnalysis(unittest.TestCase):
    """This test case downloads and analyzes all articles from
    test_articles, and each test within it checks if an attribute
    analyzed is the same as desired for all articles.
    """
    def setUp(self):
        self.articles = _downloaded_articles

    def _check_all(self, function):
        for analyzed, desired in zip(self.articles, test_articles):
            function(analyzed, desired, 
                     msg="\nError when analyzing {}".format(desired.initial_url))
    
    def test_clean_url(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['url'], desired.clean_url, msg))

    def test_domain(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['domain'], desired.domain, msg))

    def test_title(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['title'], desired.title, msg))
    
    def _check_text_equality(self, analyzed, desired, msg):
        analyzed_set = set(re.findall("[A-Za-z0-9]+", analyzed['text']))
        desired_set = set(re.findall("[A-Za-z0-9]+", desired.text))
        self.assertSetEqual(analyzed_set, desired_set, msg)

    def test_text(self):
        self._check_all(self._check_text_equality)

    def test_date(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['publish_date'], desired.publish_date, msg))

    def test_sources(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['sources']), set(desired.sources), msg))

    def test_authors(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['authors']), set(desired.authors), msg))

if __name__ == "__main__":
    unittest.main()
