"""Bengali and English two-page print layouts."""
from decimal import Decimal
import base64
from html import escape
from pathlib import Path
from bus_data import SEATS,BN,EN

FONT_DIR=Path(__file__).resolve().parent/'fonts'
RANGES={'bengali':'U+0951-0952,U+0964-0965,U+0980-09FE,U+1CD0,U+1CD2,U+1CD5-1CD6,U+1CD8,U+1CE1,U+1CEA,U+1CED,U+1CF2,U+1CF5-1CF7,U+200C-200D,U+20B9,U+25CC,U+A8F1',
 'latin':'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'}
def font_face_css():
    """Embed Noto Serif Bengali so printing works offline on any computer."""
    out=[]
    for subset,rng in RANGES.items():
        for weight in (400,600):
            f=FONT_DIR/f'noto-serif-bengali-{subset}-{weight}-normal.woff2'
            if not f.is_file():continue
            data=base64.b64encode(f.read_bytes()).decode('ascii')
            out.append(f"@font-face{{font-family:'Noto Serif Bengali';font-style:normal;font-weight:{weight};font-display:block;src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng}}}")
    return ''.join(out)

LABELS={
 'Challan No':('চালান নং','Challan no.'),'Vehicle No':('গাড়ি নং','Vehicle no.'),'Coach No':('কোচ নং','Coach no.'),'Permit No':('পারমিট নং','Permit no.'),
 'Driver':('চালক','Driver'),'Driver Mobile':('মোবাইল','Mobile'),'Guide':('গাইড','Guide'),'Guide Mobile':('মোবাইল','Mobile'),
 'Date':('তারিখ','Date'),'Time':('সময়','Time'),'Route No':('রুট নং','Route no.'),
 'Book Cash':('খাতা ক্যাশ','Book cash'),'Counter Deposit':('কাউন্টার জমা (-)','Counter deposit (-)'),
 'Refund Deposit':('রিফান্ড জমা','Refund deposit'),'Fuel Deposit':('তেল জমা (+)','Fuel deposit (+)'),
 'Wash Deposit':('ওয়াশ জমা','Wash deposit'),'B5 Deposit':('B5 জমা (-)','B5 deposit (-)'), 'Sohoj Cash':('সহজ ক্যাশ (-)','Sohoj cash (-)')}

def esc(v): return escape(str(v),quote=True)
def word(bn,en,lang): return en if lang=='en' else bn
def numeric(n,lang):
    if n is None: return '________'
    s=f'{n:,.0f}' if n==int(n) else f'{n:,.2f}'
    return s if lang=='en' else s.translate(BN)
def display(v,lang):
    s=str(v or '')
    return esc(s.translate(EN) if lang=='en' else s)

def section(trip,index,config,lang):
    d=trip['details']; outgoing=index==0
    def val(k): return display(d.get(k,''),lang) or '________'
    def field(k): return f'<div>{LABELS[k][lang=="en"]}: <b>{val(k)}</b></div>'
    name=config.get('company_name_'+lang) or word('ই-চালান','E-Challan',lang)
    address=config.get('office_address_'+lang,'');phones=config.get('office_phones','')
    if lang=='bn':phones=phones.translate(BN)
    contact=f'<p>{word("প্রধান কার্যালয়","Head office",lang)}: {esc(address)}</p>' if address else ''
    if phones:contact+=f'<p>{word("ফোন","Phone",lang)}: {esc(phones)}</p>'
    title=word('মূল চালান · যাওয়ার ট্রিপ','Main challan · Outgoing trip',lang) if outgoing else word('দ্বিতীয় চালান · আসার ট্রিপ','Secondary challan · Return trip',lang)
    metadata=''.join('<div>'+''.join(field(k) for k in col)+'</div>' for col in [['Challan No','Vehicle No','Coach No','Permit No'],['Driver','Driver Mobile','Guide','Guide Mobile'],['Date','Time','Route No']])
    from_key='From EN' if lang=='en' and d.get('From EN') else 'From';to_key='To EN' if lang=='en' and d.get('To EN') else 'To'
    route_key='Route EN' if lang=='en' and d.get('Route EN') else 'Route'
    route=f'<div class="route"><strong>{word("ট্রিপ","Trip",lang)}: {val(from_key)} → {val(to_key)}</strong><span>{word("রুট","Route",lang)}: {val(route_key)}</span></div>'
    coaster=f'<div class="coaster"><strong>{word("বাইরের কোস্টার (প্রযোজ্য হলে)","External coaster (if applicable)",lang)}</strong><div>{word("নম্বর","No.",lang)}: {val("Coaster No")} &nbsp; {word("তারিখ","Date",lang)}: {val("Coaster Date")} &nbsp; {word("সময়","Time",lang)}: {val("Coaster Time")} &nbsp; {word("ভাড়া","Fare",lang)}: {numeric(d.get("Coaster Fare",0),lang)}</div></div>'
    totals={k:Decimal(0) for k in ['Passengers','Fare BDT','Commission BDT','Net BDT']};rows=[]
    for i,seat in enumerate(SEATS):
        item=trip['seats'][seat]
        cells=['']*6
        if item:
            sign=item.get('Signature EN' if lang=='en' else 'Signature','')
            signature=f'<img class="signature-image" alt="{esc(sign)}" src="{esc(item["Signature Image"])}">' if item.get('Signature Image') else esc(sign)
            cells=[esc(item.get('Counter EN',item['Counter']) if lang=='en' else item['Counter']),numeric(1,lang),numeric(item['Fare BDT'],lang),numeric(item['Commission BDT'],lang),numeric(item['Net BDT'],lang),signature]
            for k in totals:totals[k]+=item[k]
        checker=''
        if i==0:
            checker=f'<td rowspan="37" class="checker"><div>{word("চেকার","Checker",lang)}: {val("Checker Name")}</div><p>{word("সিল ও স্বাক্ষর","Seal and signature",lang)}</p></td>'
        rows.append(f'<tr data-seat="{seat}"><td class="seat">{seat}</td>'+''.join('<td>'+c+'</td>' for c in cells)+checker+'</tr>')
    rows.append('<tr class="total"><td colspan="2">'+word('মোট','Total',lang)+'</td>'+''.join('<td>'+numeric(v,lang)+'</td>' for v in totals.values())+'<td></td></tr>')
    headings=[('সিট নং','Seat'),('কাউন্টারের নাম','Counter'),('যাওয়া' if outgoing else 'আসা','Pax'),('টাকা','Fare'),('কমিশন','Commission'),('নিট টাকা','Net'),('স্বাক্ষর','Signature'),('চেকারের সিল/স্বাক্ষর','Checker seal/signature')]
    cash=''.join(f'<div>{LABELS[k][lang=="en"]}: <b>{numeric(d.get(k,0),lang)}</b></div>' for k in ['Book Cash','Counter Deposit','Refund Deposit','Fuel Deposit','Wash Deposit','B5 Deposit','Sohoj Cash'])
    return f'''<section class="sheet {'main' if outgoing else 'secondary'}"><header><h1>{esc(name)}</h1>{contact}<div class="page-name">{title}</div></header>
    <div class="metadata">{metadata}</div>{route}{coaster}<table><colgroup><col style="width:6%"><col style="width:23%"><col style="width:6%"><col style="width:10%"><col style="width:11%"><col style="width:11%"><col style="width:13%"><col style="width:20%"></colgroup>
    <thead><tr>{''.join('<th>'+word(*h,lang)+'</th>' for h in headings)}</tr></thead><tbody>{''.join(rows)}</tbody></table>
    <div class="cash">{cash}</div><div class="signatures"><div>{word('বুকিং মাস্টারের স্বাক্ষর','Booking master signature',lang)}: __________________</div><div>{word('চালকের স্বাক্ষর','Driver signature',lang)}: __________________</div></div></section>'''

CSS='''
*{box-sizing:border-box}body{margin:0;background:#e9eef2;color:#17202a;font-family:"Noto Serif Bengali",serif}body.en{font-family:"Times New Roman","Noto Serif Bengali",serif}
.toolbar{max-width:980px;margin:18px auto;display:flex;gap:18px;align-items:center;font:14px Arial,sans-serif;padding:0 18px}.toolbar button{border:0;border-radius:5px;background:#176e8b;color:white;font:inherit;padding:13px 20px;cursor:pointer}.toolbar p{margin:0;line-height:1.5}.warning{color:#9e223d;display:none}.bn .toolbar{font-family:"Noto Serif Bengali",serif}
.sheet{--accent:#197e9a;width:190mm;margin:20px auto;background:white;box-shadow:0 3px 18px #182f4318;font-size:9pt;overflow-wrap:anywhere}.sheet.secondary{--accent:#a12d51}
header{text-align:center;padding-top:2mm;overflow:hidden;margin-bottom:2mm}h1{color:var(--accent);font-size:24pt;line-height:1.12;margin:0 0 1mm}header p{margin:0;font-size:8pt;line-height:1.4}.page-name{color:var(--accent);font-size:9pt;line-height:1.3;margin-top:1mm}
.metadata{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin-bottom:2mm}.metadata>div>div{min-height:4.7mm;line-height:1.3}.metadata b{font-weight:400}
.route{display:flex;justify-content:space-between;gap:4mm;line-height:1.35;margin-bottom:1.5mm}.route span{max-width:60%}.coaster{font-size:8pt;border-top:.2mm solid #b9c9d1;padding:1mm 0;line-height:1.3;margin-bottom:1.5mm}.coaster strong{font-weight:600}
table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8pt}th,td{border:.25mm solid #6999ac;text-align:left;vertical-align:middle;padding:.25mm .8mm;line-height:1.12}th{background:var(--accent);color:white;font-weight:400;height:6mm}td{height:4.2mm}.seat{font-family:Arial,sans-serif;font-size:7.5pt}.total td{font-weight:600}.checker{vertical-align:top;padding:3mm 2mm}.checker p{font-size:8pt;margin-top:10mm}.signature-image{max-width:100%;height:3mm;object-fit:contain;display:block}
.en .seat{font-family:"Times New Roman",serif}.cash{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5mm 4mm;margin-top:3mm;font-size:8pt;line-height:1.3}.cash b{font-weight:400}.signatures{display:flex;justify-content:space-between;gap:8mm;margin-top:5mm;padding-bottom:2mm;font-size:8pt}
@page{size:A4;margin:10mm}@media print{body{background:white}.toolbar{display:none}.sheet{margin:0;box-shadow:none;break-after:page}.sheet:last-child{break-after:auto}th{-webkit-print-color-adjust:exact;print-color-adjust:exact}.cash,.signatures,.metadata,.route,.coaster{break-inside:avoid}tr{break-inside:avoid}}
@media screen{.sheet{outline:10mm solid white;margin:18mm auto}}
'''

def document(trips,config,lang='bn'):
    if lang not in ('bn','en'):raise ValueError('Language must be bn or en.')
    button=word('প্রিন্ট / PDF','Print / Save PDF',lang)
    note=word('A4, ১০০% স্কেল। ব্রাউজারের হেডার ও ফুটার বন্ধ রাখুন।','Use A4 at 100% scale. Turn browser headers and footers off.',lang)
    warning=word('লেখা বেশি বড় হয়েছে। প্রিন্ট করার আগে পৃষ্ঠা দেখে নিন।','Long content may need extra pages. Check print preview.',lang)
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{word('ই-চালান','E-Challan',lang)}</title><style>{font_face_css()}{CSS}</style></head><body class="{lang}"><div class="toolbar"><button onclick="window.print()">{button}</button><div><p>{note}</p><p class="warning" id="fit-warning">{warning}</p></div></div>{''.join(section(t,i,config,lang) for i,t in enumerate(trips))}<script>document.fonts.ready.then(()=>{{if([...document.querySelectorAll('.sheet')].some(s=>s.offsetHeight>1046))document.getElementById('fit-warning').style.display='block';}});</script></body></html>'''
