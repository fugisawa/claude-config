"""Fixtures de JATS partilhadas pelos testes: a estrutura é a que o efetch do NCBI devolveu em 02/10/2026 para
PMC4076289, com texto inventado. O PMC declara o manuscrito do autor em `<custom-meta>` (`pmc-prop-manuscript`), e
o Europe PMC, com `is-manuscript`; o identificador NIHMS fica no XML mesmo depois que a editora substitui o
manuscrito pela versão publicada, e por isso não é a marca."""

CABECALHO = (b'<?xml version="1.0"  ?><!DOCTYPE pmc-articleset PUBLIC "-//NLM//DTD ARTICLE SET 2.0//EN" '
             b'"https://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0.dtd">')
NIHMS = b'<article-id pub-id-type="manuscript-id">NIHMS581621</article-id>'
DECLARACAO_DO_PMC = (b'<custom-meta-group><custom-meta><meta-name>pmc-prop-manuscript</meta-name>'
                     b'<meta-value>yes</meta-value></custom-meta></custom-meta-group>')
FRENTE = (b'<front><journal-meta><journal-id journal-id-type="nlm-ta">Psychol Sci</journal-id>'
          b'<journal-id journal-id-type="pmc-domain">nihpa</journal-id>'
          b'<journal-title-group><journal-title>Psychological science</journal-title></journal-title-group>'
          b'</journal-meta><article-meta><article-id pub-id-type="pmcid">PMC4076289</article-id>' + NIHMS +
          b'<article-id pub-id-type="doi">10.1177/0956797613497022</article-id>'
          b'<title-group><article-title>Developmental Reversals in Risky Decision Making</article-title></title-group>'
          b'<contrib-group><contrib contrib-type="author"><name><surname>Reyna</surname>'
          b'<given-names>Valerie F.</given-names></name></contrib></contrib-group>'
          b'<abstract><p id="P1">Agents show larger <italic toggle="yes">decision biases</italic> than students.</p>'
          b'<p id="P2">Thirty problems were presented in gain and loss frames.</p></abstract>'
          b'<kwd-group><kwd>framing</kwd></kwd-group>' + DECLARACAO_DO_PMC + b'</article-meta></front>')
CORPO = (b'<body><p id="P3">Risky decision making is a central phenomenon.</p>'
         b'<sec><title>Method</title><p>Participants were agents.</p></sec></body>')
FUNDO = (b'<back><ref-list><title>References</title><ref id="R1"><element-citation>'
         b'<article-title>Another title</article-title></element-citation></ref></ref-list></back>')
ARTIGO = b'<article article-type="research-article" xml:lang="en" dtd-version="1.4">' + FRENTE + CORPO + FUNDO + b'</article>'
ARTICLESET = CABECALHO + b'<pmc-articleset>' + ARTIGO + b'</pmc-articleset>'
# a versão da editora que guarda o NIHMS do manuscrito que ela substituiu (Sage Choice e Springer, em 02/10/2026)
VERSAO_DA_EDITORA_COM_NIHMS = ARTIGO.replace(b"<meta-value>yes", b"<meta-value>no")
MANUSCRITO_DO_EUROPEPMC = ARTIGO.replace(b"pmc-prop-manuscript", b"is-manuscript")
# o que o efetch devolve quando a editora não libera o XML: 200, folha de rosto com resumo, sem corpo
SO_A_FOLHA_DE_ROSTO = (CABECALHO + b'<pmc-articleset><article><!--The publisher of this article does not allow '
                       b'downloading of the full text in XML form.-->' + FRENTE + b'</article></pmc-articleset>')
PMCID_INEXISTENTE = (CABECALHO + b'<pmc-articleset><error id="999999999">The following PMCID is not available: '
                     b'999999999</error></pmc-articleset>')
TEXTO_DO_ARTIGO = ("Developmental Reversals in Risky Decision Making\n\n"
                   "Agents show larger decision biases than students.\n\n"
                   "Thirty problems were presented in gain and loss frames.\n\n"
                   "Risky decision making is a central phenomenon.\n\nMethod\n\nParticipants were agents.")
