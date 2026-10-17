<p align="center"><img src="assets/logo.png" alt="Hanif Enterprise" width="360"></p>

# Bus Challan Autofiller

Version 1.3.0 · see [CHANGELOG.md](CHANGELOG.md)

Generates numbered bus challans in Bengali and English. Each challan has a **Main** form (outgoing trip) and a **Secondary** form (return trip) that share one challan number. Every page carries 36 seats, A-1 to I-4.

Each form header shows the red company symbol before the company name, and the same symbol appears as a very faint watermark behind the table. All text inside the table is centered.

Bengali prints use **Noto Serif Bengali**, bundled inside the app, so the forms look the same on any computer, online or offline. English prints use Times New Roman. The company name, head office and phone numbers come from `settings.json`. No passenger, driver or transaction data from old samples is included.

## Quick start

1. Extract the ZIP. On Windows you need Python 3.10+ with pip and Tcl/Tk.
2. Run `setup.cmd` once. It installs the libraries for reading Excel files and signature images, so it needs an internet connection.
3. Open `challan_input.xlsx`. In the **Counters** sheet, enter your real counter names first. Then fill in **Trip Details**, and pick a counter for each seat in **Main** and **Secondary**. Save the file.
4. Run `run.cmd`, choose a language, and click **Save NEW challan**.
5. Pick an output folder. Both language versions are saved, and the language you selected opens in your browser.
6. Click **Print / PDF**, choose A4 and 100% scale, and turn off the browser's header and footer.

To see an empty form, click **Blank forms** or open one of the sample PDFs. Blank forms do not use up a challan number.

## Challan numbers and reprinting

- Each new challan gets the next number: `01/2026`, `02/2026`, `03/2026` and so on. Bengali forms show the same number in Bengali digits.
- Main and Secondary share the number, and so do both languages.
- The year comes from the Main trip date. A new year restarts the serial at 01.
- To print an old challan again, use **Reprint saved** or open the saved HTML file. This never creates a new number. Clicking **Save NEW** again with the same workbook creates a new challan with a new number.
- Numbers and the saved forms live in `challan-register.sqlite3` in the app folder. Keep this file when you move or back up the folder, and keep it when you upgrade to a new version.
- The register is local. To continue the same serial, keep using the same register. Registers on different computers do not sync.
- A saved challan does not change if you later edit routes, counters or company settings. Reprint always uses the saved form.

## Routes sheet

Dhaka–Chattogram at 300 BDT is already included, and the return fare on this route is the same. Add more routes in rows 5 to 104 (up to 100).

Fill in `Route`, `From`, `To` and `Fare BDT`. If you fill in `Route EN`, `From EN` and `To EN`, those appear on English prints; otherwise the original text is used. `Route No` is a separate optional number. The gray `Status` cell shows Ready when the row is valid.

On Trip Details, choose the Main route from the dropdown. The return route is the reverse, automatically. Both forms use the same route and fare.

## Counters sheet

Real counter names and commission rates were not available, so nothing here is guessed. List your counters in rows 5 to 104. They then appear in the Main and Secondary dropdowns.

| Column | Use |
|---|---|
| Counter | Counter name. Must be unique. |
| Commission Mode | Empty or None = no commission. Fixed = a set amount per passenger. Percent = a percentage of the fare. |
| Rate | Amount in BDT for Fixed. For Percent, 10 means 10%. Use 0 or leave empty when there is no commission. |
| Signatory | Name of the person who signs, if needed. |
| Signature File | File name or full path of your own authorized PNG/JPEG signature image. |
| Counter EN / Signatory EN | Optional names for English prints. |
| Status | Automatic check. Fix any error before saving a challan. |

Only Fixed and Percent counters have commission deducted. Percentage commission is rounded to two decimal places. A challan is not created if the commission is larger than the fare.

## Main and Secondary

- Choosing a Counter for a seat sets **Passengers = 1** and fills in the route fare, that counter's commission, the net amount and the signatory name. For several passengers, fill in the Counter for each of those seats.
- Leave the Counter empty for empty seats. Do not edit the gray calculation cells in columns C to G.
- If a seat needs a different fare, enter it in **Fare Override**. Zero is allowed. If it is empty, the route fare applies.
- The Excel file has live formulas. Before printing, Python recalculates everything from the source values. It does not trust old formula caches or totals that were edited by hand.
- Keep all seats from A-1 to I-4. Even if you reorder the rows, the print follows the normal seat order.
- The checker gets one large seal-and-signature cell instead of a cell per seat.
- Each form ends with two signature lines: Booking master and Manager.

## Trip Details

Yellow cells are input. Gray cells are automatic or shared. Enter vehicle, coach, permit, guide, guide phone, checker name and route once in Main, and they carry over to both forms. The driver and driver phone also carry over, but Secondary accepts a replacement driver.

If you enter a new driver name in Secondary, enter that driver's phone too. If you give a new name and leave the phone empty, the old driver's phone is not copied.

Set the **Date and Time for each trip separately**. Excel dates or `YYYY-MM-DD` are accepted, and Excel times or `HH:MM` (24-hour). Store numbers and phone numbers as text so a leading 0 is not lost.

If an outside vehicle is taken, fill in **Coaster No, Coaster Date, Coaster Time and Coaster Fare** on the matching trip. If you enter a Coaster No, the date and time are required. If no vehicle is taken, leave the number, date and time empty and the fare at 0.

Book Cash, Counter Deposit, Refund Deposit, Fuel Deposit, Wash Deposit, B5 Deposit and Sohoj Cash start at 0. Enter your own amounts when needed. They are separate deposit records. No extra cash-settlement calculation is added.

## Fixed signatures: Booking master, Manager and Checker

Put three signature images in the `signatures/` folder with exactly these names:

| File | Appears |
|---|---|
| `booking-master.png` | Above the "Booking master signature" line at the bottom |
| `manager.png` | Above the "Manager signature" line at the bottom |
| `checker.png` | In the checker cell, above "Seal and signature" |

`.jpg` and `.jpeg` also work. A PNG with a transparent background looks best. Each image must be under 2 MB and at most 4000 pixels. They are added to every new challan, in both languages and on both Main and Secondary, with no extra clicks.

If a file is missing, that line stays blank for hand signing. To keep the images somewhere else, set `booking_master_signature`, `manager_signature` or `checker_signature` in `settings.json` to a file path. If a path is set but the file does not exist, the app stops with a clear message instead of printing a blank line.

The checker image is one fixed image for both trips. Use **Draw signature** to create the PNGs. Only use signatures of people who have authorized this.

## Counter signatures

These are the per-seat counter signatures. Click **Draw signature** to open the local signature pad. Draw your authorized signature with a mouse, finger or pen, then save it as a PNG. Put the file next to the Excel file and enter its name in `Signature File` on the Counters sheet. You can also use an existing PNG or JPEG (under 2 MB, at most 4000 pixels).

When that counter is chosen, the image is placed in the signature cell of the matching seat. Without an image, the Signatory name is shown. Without a name, the cell stays empty. Nothing is made up. This places a picture of a signature and does not add any cryptographic certificate. Everything runs locally, and the signature pad uploads nothing.

## Company information and language

Edit `settings.json` to change the Bengali and English company name, office address and phone numbers. Names of people are not translated automatically. They print exactly as you type them. Routes and counters have separate English columns.

Every new challan produces `main-and-secondary-bn.html` and `main-and-secondary-en.html`. Both open offline. In each language, Main comes first and Secondary second. If you enter long text, check the print preview.

## Logo

The `assets/` folder holds `logo.png` (full logo, used in this README), `logo-symbol.png` (red symbol, used as the watermark) and `logo-symbol-small.png` (red symbol, used beside the company name). To change the logo, replace the two symbol files with your own PNGs (square, transparent background). If a file is missing, that element is simply left out. Images are embedded in every generated HTML file.

## Fonts

The `fonts/` folder contains Noto Serif Bengali (regular and semi-bold, Bengali and Latin subsets) as WOFF2 files. They are embedded into every generated HTML file, so no font installation is needed. The font is by the Noto Project Authors and is licensed under the SIL Open Font License 1.1. See `fonts/OFL-LICENSE.txt`. Keep the `fonts/` folder next to the Python files.

## Command line

```text
python challan_autofill.py challan_input.xlsx --out generated --language bn --open
python challan_autofill.py --reprint 01/2026 --out generated --language en --open
python challan_autofill.py --blank --out generated
python challan_autofill.py --version
python -m unittest discover -s tests -v
```

## Author

Developed by **Kazi Shakib**.

## License

The source code is released under the [MIT License](LICENSE). Copyright (c) 2026 Kazi Shakib.

The MIT License covers the source code only. The bundled Noto Serif Bengali font keeps its own license, the SIL Open Font License 1.1 (`fonts/OFL-LICENSE.txt`). The company name and details in `settings.json` belong to their owner and are not licensed for reuse.
