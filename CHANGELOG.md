# Changelog

## 1.3.1 - 2026-10-17
- Renamed `challan_autofill.py` to `challan-autofill.py`, `challan_input.xlsx` to `challan-input.xlsx` and `START_HERE.txt` to `START-HERE.txt`. Python modules keep underscores because Python cannot import hyphenated names.

## 1.3.0 - 2026-10-17
- Booking master, Manager and Checker signature images are added to every challan automatically from the `signatures/` folder (or paths in `settings.json`).
- Missing images leave the line blank; a configured but missing file stops with a clear error.
- New tests for the fixed signatures.

## 1.2.1 - 2026-10-17
- Heading logo made larger.

## 1.2.0 - 2026-10-17
- Red company symbol added before the company name in the form heading.
- Same symbol added as a very faint page-background watermark.
- All text inside the table is now centered.
- Added `assets/` folder with the logo files; README shows the logo.

## 1.1.1 - 2026-10-17
- Bottom signature line is now "Booking master signature" and "Manager signature". The driver signature line was removed.

## 1.1.0 - 2026-10-16
- Bengali prints now use Noto Serif Bengali, bundled in `fonts/` and embedded in every generated HTML file.
- README and START-HERE rewritten in English.
- Added MIT License and font license notice.
- Added `--version` command-line option and version shown in the app window title.
- Sample PDFs and HTML regenerated with the new font.

## 1.0.0 - 2026-04 (first version)
- Numbered Main and Secondary challans in Bengali and English.
- Excel input, counter commissions, signature images, local reprint register.
