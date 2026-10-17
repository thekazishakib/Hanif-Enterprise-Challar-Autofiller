"""Save numbered bilingual bus challans, or reprint a saved pair unchanged."""
import argparse,json,sys,tempfile,webbrowser
from pathlib import Path
from bus_data import InputError,load_data,blank_data,save_numbered,list_saved,saved_html,role_signatures
from print_forms import document
from version import __version__
BASE=Path(__file__).resolve().parent
REGISTRY=BASE/'challan-register.sqlite3'

def load_config(path):
    config=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(config,dict) or any(not isinstance(v,str) for v in config.values()):
        raise InputError('Company settings must be text.')
    return config

def with_signatures(config):
    """Copy of the settings plus embedded Booking master / Manager / Checker signature images."""
    config=dict(config)
    for role,image in role_signatures(config,BASE).items(): config['sig_'+role]=image
    return config

def export_pair(htmls,parent,prefix):
    parent=Path(parent).resolve();parent.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(prefix=prefix.replace('/','-')+'-',dir=parent))
    paths={}
    for lang,html in htmls.items():
        paths[lang]=folder/f'main-and-secondary-{lang}.html'
        paths[lang].write_text(html,encoding='utf-8')
    return paths

def generate(input_path,output_parent,config_path=BASE/'settings.json',blank=False,registry=REGISTRY):
    config=with_signatures(load_config(config_path))
    if blank:
        return export_pair({lang:document(blank_data(),config,lang) for lang in ['bn','en']},output_parent,'blank-forms')
    trips=load_data(input_path)  # All validation happens before reserving a number.
    Path(output_parent).mkdir(parents=True,exist_ok=True)
    number,htmls=save_numbered(trips,config,document,registry)
    try:return export_pair(htmls,output_parent,number)
    except OSError as exc:
        raise InputError(f'Challan {number} is saved in the register, but export failed. Use Reprint after choosing a writable output folder.') from exc

def reprint(number,parent,registry=REGISTRY):
    return export_pair({lang:saved_html(registry,number,lang) for lang in ['bn','en']},parent,'reprint-'+number)

def gui():
    import tkinter as tk
    from tkinter import filedialog,messagebox,ttk
    root=tk.Tk();root.title(f'Bus challan / বাস চালান  v{__version__}');root.geometry('800x510')
    f=ttk.Frame(root,padding=24);f.pack(fill='both',expand=True)
    ttk.Label(f,text='বাস চালান · বাংলা / English',font=('Nirmala UI',18,'bold')).pack(anchor='w')
    ttk.Label(f,text='Fill Trip Details, choose counters in Main / Secondary, then save the workbook.').pack(anchor='w',pady=(8,14))
    chosen=tk.StringVar(value=str(BASE/'challan_input.xlsx'));ttk.Entry(f,textvariable=chosen,width=95).pack(fill='x')
    def choose():
        p=filedialog.askopenfilename(filetypes=[('Excel workbook','*.xlsx')],initialdir=BASE)
        if p:chosen.set(p)
    ttk.Button(f,text='Excel ফাইল বাছুন / Choose workbook',command=choose).pack(anchor='w',pady=8)
    lang=tk.StringVar(value='bn');row=ttk.Frame(f);row.pack(anchor='w')
    ttk.Radiobutton(row,text='বাংলা',variable=lang,value='bn').pack(side='left');ttk.Radiobutton(row,text='English',variable=lang,value='en').pack(side='left',padx=15)
    def show(paths):
        webbrowser.open(paths[lang.get()].as_uri())
        messagebox.showinfo('Saved / সংরক্ষিত',f'Both languages saved in:\n{paths[lang.get()].parent}\n\nReprint this saved file to keep the same challan number.')
    def run(blank=False):
        parent=filedialog.askdirectory(title='Output folder',initialdir=BASE)
        if not parent:return
        try:show(generate(chosen.get(),parent,blank=blank))
        except Exception as exc:messagebox.showerror('Please check / তথ্য দেখুন',str(exc))
    ttk.Button(f,text='নতুন চালান সংরক্ষণ / Save NEW challan',command=run).pack(anchor='w',pady=(15,6))
    ttk.Label(f,text='New save = next number. Reprint = same number. Main and Secondary always share it.').pack(anchor='w')
    def reopen():
        records=list_saved(REGISTRY)
        if not records:messagebox.showinfo('Saved challans','No saved challans yet.');return
        dialog=tk.Toplevel(root);dialog.title('Reprint saved challan');dialog.geometry('470x350')
        box=tk.Listbox(dialog);box.pack(fill='both',expand=True,padx=15,pady=15)
        for num,created in records:box.insert('end',num+'    '+created)
        def open_record():
            selected=box.curselection()
            if not selected:return
            try:show(reprint(records[selected[0]][0],BASE/'generated'))
            except Exception as exc:messagebox.showerror('Reprint',str(exc))
        ttk.Button(dialog,text='Open / খুলুন',command=open_record).pack(pady=10)
    ttk.Button(f,text='আগের চালান পুনরায় প্রিন্ট / Reprint saved',command=reopen).pack(anchor='w',pady=8)
    ttk.Button(f,text='ফাঁকা ফরম দেখুন / Blank forms',command=lambda:run(True)).pack(anchor='w',pady=5)
    ttk.Button(f,text='স্বাক্ষর আঁকুন / Draw signature',command=lambda:webbrowser.open((BASE/'signature-pad.html').as_uri())).pack(anchor='w',pady=5)
    root.mainloop()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',nargs='?',type=Path)
    p.add_argument('--out',type=Path,default=BASE/'generated');p.add_argument('--config',type=Path,default=BASE/'settings.json')
    p.add_argument('--blank',action='store_true');p.add_argument('--reprint');p.add_argument('--language',choices=['bn','en'],default='bn');p.add_argument('--open',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {__version__}')
    args=p.parse_args()
    if not args.input and not args.blank and not args.reprint:gui();return 0
    try:paths=reprint(args.reprint,args.out) if args.reprint else generate(args.input,args.out,args.config,blank=args.blank)
    except Exception as exc:print(f'Could not create challan: {exc}',file=sys.stderr);return 1
    for lang,path in paths.items():print(lang+': '+str(path))
    if args.open:webbrowser.open(paths[args.language].as_uri())
    return 0

if __name__=='__main__':raise SystemExit(main())
