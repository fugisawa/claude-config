# OCR — não é aqui

Página de PDF sem camada de texto (o `validate_pdf.py` acusa cobertura de texto abaixo de
100%) é caso da skill **`ocr-com-evidencia`**, que decide entre a visão direta do Claude e os
motores locais, mantém candidatos e evidência, e só promove a transcrição depois da revisão.

O que esta skill faz por você antes de sair daqui é renderizar as páginas:

```bash
pdftoppm -r 300 -png -f 1 -l 5 documento.pdf paginas/pagina   # páginas 1–5 → paginas/pagina-1.png …
```

Depois, siga `ocr-com-evidencia` com a pasta `paginas/` como entrada. Este arquivo era um guia
genérico de `pytesseract` (inglês, espanhol, sem português, sem foto de página) e foi reduzido a
este ponteiro em 06/09/2026 para que o OCR tenha um dono só.
