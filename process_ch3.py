import pandas as pd, numpy as np, json, re, collections
def T(v):
    try:
        return float(v)==1.0
    except Exception:
        return False

EDITIONS=[2007,2009,2010,2012,2014,2016,2021,2022,2024,2026]
# champions (public record, famous-8 relevant)
CHAMP={2007:"India",2009:"Pakistan",2010:"England",2012:"West Indies",2014:"Sri Lanka",
       2016:"West Indies",2021:"Australia",2022:"England",2024:"India",2026:"India"}

ABBR={"SA":"South Africa","WI":"West Indies","NZ":"New Zealand","SL":"Sri Lanka","UAE":"UAE",
      "Aus":"Australia","Eng":"England","Pak":"Pakistan","Ind":"India","RSA":"South Africa",
      "Ban":"Bangladesh","Afg":"Afghanistan","Zim":"Zimbabwe","Ire":"Ireland","Net":"Netherlands","Nam":"Namibia",
      "Sco":"Scotland","HK":"Hong Kong","PNG":"Papua New Guinea","Uga":"Uganda","Can":"Canada","USA":"USA","Nep":"Nepal","Oman":"Oman"}
def norm_team(s):
    s=str(s).strip()
    return ABBR.get(s,s)
KNOWN_TEAMS=["South Africa","West Indies","New Zealand","Sri Lanka","United States Of America","United Arab Emirates","Papua New Guinea","Hong Kong","India","Australia","England","Pakistan","Bangladesh","Afghanistan","Zimbabwe","Ireland","Netherlands","Namibia","Scotland","Uganda","Canada","Nepal","Oman","Kenya","USA","UAE"]
NORMALIZE={"United States Of America":"USA","United Arab Emirates":"UAE"}
def teams_from(label):
    lab=str(label)
    found=[]
    low=lab.lower()
    for t in KNOWN_TEAMS:
        if t.lower() in low:
            nm=NORMALIZE.get(t,t)
            if nm not in found: found.append(nm)
    return found

# ---- unify both sources into ball rows ----
rows=[]  # year, match, batsman, bowler, bat_runs, legal, four, six, wkt, over, comm
com=pd.read_csv("/mnt/user-data/uploads/all_t20_worldcup_commentary_2007_2026__1_.csv")
com["year"]=pd.to_numeric(com["year"],errors="coerce")
for r in com.itertuples(index=False):
    y=r.year
    if pd.isna(y): continue
    y=int(y)
    wide=T(getattr(r,"isWide",0)); nb=T(getattr(r,"isNoBall",0))
    runs=float(getattr(r,"runs",0) or 0)
    bat_runs=0 if wide else runs
    rows.append({"year":y,"match":r.match,"batsman":str(r.batsman),"bowler":str(r.bowler),
        "bat_runs":bat_runs,"legal":(not wide and not nb),
        "four":T(getattr(r,"isFour",0)),"six":T(getattr(r,"isSix",0)),
        "wkt":(", OUT" in str(getattr(r,"shortText","") or "").upper()),"over":float(getattr(r,"over",0) or 0),
        "comm":str(getattr(r,"commentary","") or ""),"bat_team":None})

x=pd.read_excel("wc24/T20_WC_24_All_Matches_Dataset.xlsx")
for r in x.itertuples(index=False):
    wide=T(getattr(r,"isWide",0)); nb=T(getattr(r,"isNoBall",0))
    br=float(getattr(r,"batsmanRuns",0) or 0)
    rows.append({"year":2024,"match":r.match,"batsman":str(r.batsmanName),"bowler":str(r.bowlerName),
        "bat_runs":br,"legal":(not wide and not nb),
        "four":(T(getattr(r,"isBoundary",0)) and br==4),"six":(T(getattr(r,"isBoundary",0)) and br==6),
        "wkt":T(getattr(r,"isBowlerWicket",0)),"over":float(getattr(r,"over",0) or 0),
        "comm":str(getattr(r,"commentary","") or ""),"bat_team":norm_team(getattr(r,"currentInning",""))})
df=pd.DataFrame(rows)
df=df[df.year.isin(EDITIONS)]
print("total balls:",len(df),"| years:",sorted(df.year.unique()))

# ---- player -> country (team common to ALL their matches) ----
def country_map(sub):
    appear=collections.defaultdict(list)  # player -> list of team-sets
    for m in sub["match"].dropna().unique():
        ts=set(teams_from(m))
        for p in set(sub[sub["match"]==m]["batsman"]).union(set(sub[sub["match"]==m]["bowler"])):
            appear[p].append(ts)
    out={}
    for p,sets in appear.items():
        inter=set.intersection(*sets) if sets else set()
        if len(inter)==1: out[p]=list(inter)[0]
        else:
            # fallback: most common team across their matches
            cnt=collections.Counter()
            for s in sets:
                for t in s: cnt[t]+=1
            out[p]=cnt.most_common(1)[0][0] if cnt else "Unknown"
    return out

# ---- wagon zones from commentary ----
ZONE_KW=[("Third man",["third man","third-man"]),("Point",["point","backward point","cover point","gully"]),
 ("Covers",["cover","covers","extra cover"]),("Long-off",["long-off","long off","mid-off","mid off","straight down","down the ground"]),
 ("Long-on",["long-on","long on","mid-on","mid on"]),("Mid-wicket",["mid-wicket","midwicket","mid wicket","wide long-on"]),
 ("Square leg",["square leg","square-leg","deep square","backward square"]),("Fine leg",["fine leg","fine-leg","leg glance","flick","down leg","long leg"])]
def zone_of(text):
    t=text.lower()
    for z,kws in ZONE_KW:
        for k in kws:
            if k in t: return z
    return None
def length_of(t):
    t=t.lower()
    if any(k in t for k in ["yorker","full toss","low full","blockhole","block hole"]): return "Yorker"
    if any(k in t for k in ["half-volley","half volley","overpitched","pitched up","fuller","full delivery","full ball","full outside","full and","full,","drove","driven","on the full"]): return "Full"
    if any(k in t for k in ["short","bouncer","pull","hook","back of a length","back of length","banged in","climbs","rising","chest high","shorter"]): return "Short"
    if any(k in t for k in ["good length","good areas","length ball","on a length","nagging","good length","just short of a length","hard length"]): return "Good"
    return None
def line_of(t):
    t=t.lower()
    if any(k in t for k in ["down leg","leg stump","on the pads","onto the pads","leg side","flicked","flick","glance","tucked","into the pads","on the leg","wide down leg"]): return "Leg"
    if any(k in t for k in ["outside off","off stump","fourth stump","fifth stump","wide of off","channel","off side","wide outside","width","angling across","away from"]): return "Off"
    if any(k in t for k in ["middle stump","off and middle","middle and leg","straight","on the stumps","at the stumps","middle of"]): return "Straight"
    return None
def phase_of(over):
    o=int(over)  # 0-based over number
    if o<6: return "Powerplay"
    if o<15: return "Middle"
    return "Death"

OUT={}
for y in EDITIONS:
    sub=df[df.year==y]
    if len(sub)==0:
        OUT[str(y)]={"champion":CHAMP[y],"players":[],"country_counts":{}}; continue
    cmap=country_map(sub)
    # batting agg
    bat=collections.defaultdict(lambda:{"runs":0,"balls":0,"f":0,"s":0,"zone":collections.Counter()})
    for r in sub.itertuples(index=False):
        b=bat[r.batsman]; b["runs"]+=r.bat_runs
        if r.legal: b["balls"]+=1
        if r.four: b["f"]+=1
        if r.six: b["s"]+=1
        if r.bat_runs>0:
            z=zone_of(r.comm)
            if z: b["zone"][z]+=r.bat_runs
    # bowling agg
    bowl=collections.defaultdict(lambda:{"balls":0,"conc":0,"wkts":0,"dots":0,"phase":collections.defaultdict(lambda:{"runs":0,"wkts":0,"balls":0})})
    for r in sub.itertuples(index=False):
        bw=bowl[r.bowler]
        if r.legal: bw["balls"]+=1
        bw["conc"]+=0  # placeholder; commentary 'runs' total approximates conceded
        if r.wkt: bw["wkts"]+=1
        ph=phase_of(r.over); bw["phase"][ph]["balls"]+= (1 if r.legal else 0)
        if r.wkt: bw["phase"][ph]["wkts"]+=1
    # conceded: need total runs off bowler -> recompute from 'runs' (use bat_runs+ approx). Use raw runs per ball:
    conc=collections.defaultdict(float); phc=collections.defaultdict(lambda:collections.defaultdict(float))
    bgrid=collections.defaultdict(dict); bwk=collections.defaultdict(dict)
    for r in sub.itertuples(index=False):
        conc[r.bowler]+=r.bat_runs  # approx conceded (off the bat); extras minor
        phc[r.bowler][phase_of(r.over)]+=r.bat_runs
        if r.bat_runs==0 and r.legal: bowl[r.bowler]["dots"]+=1
        if r.legal:
            ln=length_of(r.comm); li=line_of(r.comm)
            if ln and li:
                gk=ln+"|"+li
                bgrid[r.bowler][gk]=bgrid[r.bowler].get(gk,0)+1
                if r.wkt: bwk[r.bowler][gk]=bwk[r.bowler].get(gk,0)+1
    for bn in bowl: bowl[bn]["conc"]=conc[bn]
    for bn in bowl:
        for ph in bowl[bn]["phase"]:
            bowl[bn]["phase"][ph]["runs"]=phc[bn][ph]

    # tournament average economy this year
    tot_runs=sum(r.bat_runs for r in sub.itertuples(index=False))
    tot_legal=sum(1 for r in sub.itertuples(index=False) if r.legal)
    avg_econ=(tot_runs/(tot_legal/6)) if tot_legal else 8.0
    # batters
    batters=[]
    for name,b in bat.items():
        if b["balls"]<10: continue
        sr=b["runs"]/b["balls"]*100 if b["balls"] else 0
        bi=b["runs"]+(b["f"]+b["s"])*2+max(0,sr-120)*b["balls"]/100
        batters.append({"name":name,"country":cmap.get(name,"Unknown"),"role":"bat","impact":round(bi,1),
            "runs":int(b["runs"]),"balls":b["balls"],"sr":round(sr),"f":b["f"],"s":b["s"],"wagon":dict(b["zone"])})
    batters.sort(key=lambda p:-p["impact"]); batters=batters[:5]
    # bowlers (runs-saved + wicket value)
    bowlers=[]
    for name,bw in bowl.items():
        if bw["balls"]<12: continue
        overs=bw["balls"]/6; econ=bw["conc"]/overs if overs else 0
        bi=bw["wkts"]*20+(avg_econ-econ)*overs+bw["dots"]*0.3
        ph={k:{"runs":round(v["runs"]),"wkts":v["wkts"],"balls":v["balls"]} for k,v in bw["phase"].items()}
        bowlers.append({"name":name,"country":cmap.get(name,"Unknown"),"role":"bowl","impact":round(bi,1),
            "wkts":bw["wkts"],"econ":round(econ,1),"conceded":int(bw["conc"]),"overs":round(overs,1),"phases":ph,
            "grid":bgrid.get(name,{}),"wgrid":bwk.get(name,{})})
    bowlers.sort(key=lambda p:-p["impact"]); bowlers=bowlers[:5]
    # normalize impact within each list to 0-100 for bar widths
    if batters:
        mb=max(p["impact"] for p in batters) or 1
        for p in batters: p["bar"]=round(p["impact"]/mb*100,1)
    if bowlers:
        mw=max(p["impact"] for p in bowlers) or 1
        for p in bowlers: p["bar"]=round(p["impact"]/mw*100,1)
    cc=collections.Counter([p["country"] for p in batters+bowlers])
    OUT[str(y)]={"champion":CHAMP[y],"batters":batters,"bowlers":bowlers,"country_counts":dict(cc)}
    print(f"{y}: champ={CHAMP[y]} | bat1={batters[0]['name'] if batters else '-'} | bowl1={bowlers[0]['name'] if bowlers else '-'}({bowlers[0]['country'] if bowlers else ''}) | countries={dict(cc)}")

json.dump(OUT,open("ch3_data.json","w"))
open("ch3_data_final.js","w").write("const PLAYER_DATA = "+json.dumps(OUT,separators=(",",":"))+";")
print("\nsaved ch3_data.json (",round(len(open('ch3_data_final.js').read())/1024),"KB )")
