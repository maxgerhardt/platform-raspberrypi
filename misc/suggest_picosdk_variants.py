import os, json, glob, difflib, re

boards_dir = os.path.abspath("boards")
headers_dir = r"C:\Users\Max\.platformio\packages\framework-picosdk\src\boards\include\boards"
output_file = "board_check_results.json"

json_files = glob.glob(os.path.join(boards_dir, "*.json"))
available_headers = {os.path.splitext(f)[0]: f for f in os.listdir(headers_dir) if f.endswith(".h")}
equivalence_dict = {"5100s": ["w5100s"]}

def in_equivalence(w,t): return w in t or any(eq in t for eq in equivalence_dict.get(w,[]))
def special_mismatch(o,c):
    for g in [["5100s","w5100s"]]:
        if any(in_equivalence(x,o) for x in g)!=any(in_equivalence(x,c) for x in g): return True
    for m in ["5500","55rp20","6300","wizfi360"]:
        if m in o and m not in c: return True
    return False
def mcu_from_header(h):
    try:
        t=open(os.path.join(headers_dir,h)).read()
        m=re.search(r"pico_board_cmake_set\s*\(\s*PICO_PLATFORM\s*,\s*(rp2040|rp2350)\s*\)",t)
        return m.group(1) if m else None
    except: return None
def mcu_mismatch(mcu,f):
    d=mcu_from_header(f)
    return d and d!=mcu
def norm(v):
    if v=="rpipico": return "pico"
    if v=="generic_rp2350": return "pico2"
    return v
def subs(v):
    v=v.replace("rpipico2","pico2")
    v=re.sub(r'_pico2$', '.pico2', v)
    v=re.sub(r'_connect$', '_rp2040_connect', v)
    return v
def suggest(v,mcu):
    v=subs(norm(v))
    for alt in [v.replace("_",".",1),v.replace("_",".")]:
        if alt in available_headers and not mcu_mismatch(mcu,available_headers[alt]) and not special_mismatch(v,alt): return available_headers[alt]
    for m in difflib.get_close_matches(v,available_headers.keys(),n=5,cutoff=0.7):
        f=available_headers[m]
        if not mcu_mismatch(mcu,f) and not special_mismatch(v,m): return f
    return None

found,suggested,not_found={}, {},[]
for jf in json_files:
    bn=os.path.basename(jf)
    name=os.path.splitext(bn)[0]
    try:
        d=json.load(open(jf))
        variant=d.get("build",{}).get("variant")
        mcu=d.get("build",{}).get("mcu","").lower()
        for cand in [name,variant]:
            if not cand: continue
            vn=subs(norm(cand))
            if vn in available_headers and not mcu_mismatch(mcu,available_headers[vn]):
                found[bn]=available_headers[vn]; break
            s=suggest(cand,mcu)
            if s: 
                suggested[bn]=s
                print(f"[SUGGEST] {cand}.h (MCU={mcu}) → {s} (PICO_PLATFORM={mcu_from_header(s)})")
                break
        else: not_found.append(bn)
    except: not_found.append(bn)

if not_found: print("\nMissing:"); [print(" ",v) for v in sorted(set(not_found))]
else: print("✅ All variants matched.")

print("\nFound:",json.dumps(found,indent=2))
print("\nSuggested:",json.dumps(suggested,indent=2))
print("\nNot found:",json.dumps(not_found,indent=2))
json.dump({"found":found,"suggested":suggested,"not found":not_found},open(output_file,"w"),indent=2)
