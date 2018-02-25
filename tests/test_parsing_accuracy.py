import unittest
import re

import scrapy
from datetime import date

from factscraper import analyze_url, downloader

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
        [])]

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


# Download them now so we don't have to redownload them for each test
_downloaded_articles = [analyze_url(article.initial_url)
                        for article in test_articles]

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
